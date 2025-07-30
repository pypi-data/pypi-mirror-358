import json
import logging
import mimetypes
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
from pathlib import Path
from tqdm import tqdm
from unittest.mock import Mock

from article.utils import convert_markdown_to_text, format_nav_path, to_str
from publisher import PublisherManager
from utils.access import DriveManager
from utils.json import EntityManager
from utils.text import HTMLRequestHelper, URLHelper, expand_to_list


log = logging.getLogger(__name__)


class StopWords(Enum):
  PAYWALL = 'paywall'
  PREMIUM = 'premium'
  SUBSCRIPTION = 'subscription'


@dataclass(frozen=True)
class RegexConfig:
  WILDCARD: str = r'.*?'
  FLAG: str = r'REGEX:'
  JSON_LD: str = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
  HEADLINE: str = r'^# '


class ArticleLoader:
  """loads article from raw html with metadata extraction"""

  # custom extraction settings
  _config_dir = Path(__file__).parent.parent / 'config'
  CUSTOM_PARSE: str = _config_dir / 'parse_custom.json'

  # http request constants
  _DEFAULT_STOP_WORDS = [word.value for word in StopWords]

  # parse thresholds
  _MIN_TAG_PAIRS = 2

  # regex patterns
  _CSS_PREFIXES = ('.', '#', '[', 'meta', 'div', 'span', 'h1', 'h2', 'h3' )

  def __init__(self,
               drive_manager: Optional[DriveManager] = None,
               publisher_manager: Optional[PublisherManager] = None,
               timeout: int = HTMLRequestHelper.DEFAULT_TIMEOUT,
               sleep: int = HTMLRequestHelper.DEFAULT_SLEEP,
               max_retries: int = HTMLRequestHelper.DEFAULT_MAX_RETRIES,
               custom_parse: Optional[Union[str, Dict[str, Any]]] = None,
               stop_words: Optional[List[str]] = _DEFAULT_STOP_WORDS):
    # check each manager individually
    if drive_manager is None:
      raise ValueError("drive_manager required")
    if not isinstance(drive_manager, (DriveManager, Mock)):
      raise ValueError("drive_manager must be DriveManager or Mock")

    if publisher_manager is None:
      raise ValueError("publisher_manager required")  
    if not isinstance(publisher_manager, (PublisherManager, Mock)):
      raise ValueError("publisher_manager must be PublisherManager or Mock")

    self.drive_manager = drive_manager
    self._publisher_manager = publisher_manager

    self._timeout = timeout
    self._sleep = sleep
    self._max_retries = max_retries

    default = self.drive_manager.config.DEFAULT_PARSE
    custom = custom_parse or (
             self.drive_manager.config.DIR_SYSTEM / self.CUSTOM_PARSE)
    self._entity_manager = EntityManager(drive_manager, default, custom)
    self._stop_words = stop_words or self._DEFAULT_STOP_WORDS

    self._setup_article_fields()
    self._setup_html_converter()

  # public interface methods
  def process_keys(self, keys: Union[str, List[str]]) -> None:
      keys = expand_to_list(keys)
      for key in tqdm(keys, desc='processing keys', ncols=80, ascii=True):
          self.process_one(key)

  def process_one(self, source: str):
    if source.startswith("https://"):
      log.info(f"downloading article from URL: {source}")
      article = self.download(source)
    else:
      log.info(f"loading article from file: {source}")
      article = self.load_from_file(source)

    # process the article
    if article and article.html:
      ok = self.process_article(article)
      if ok:
        log.info("article processing completed successfully")
      else:
        log.error("article processing failed")
    else:
      log.error("failed to load article")

  def process_article(self, article: Article):
    """process a single article and save results"""
    if not article:
      log.error("no article to process")
      return False

    # parse the article
    ok = self.parse(article)
    if not ok:
      log.error("failed to parse article")
      return False

    log.info(f'html: {len(article.html)} text: {len(article.text)}')

    # extract NLP features
    ok = self.extract_nlp_features(article)
    if not ok:
      log.warning("failed to extract NLP features")

    # set nav_key if not present
    if not hasattr(article, 'nav_key') or not article.nav_key:
      now = datetime.now()
      article.nav_key = f"{now.year}-{now.month:02d}-000"

    # log article info
    log.info(to_str(article, prove_its_useless=True, shorter=True))

    # save processed files
    if article.text:
      file_path = article.nav_key + '.txt'
      file_path = self.drive_manager.config.DIR_CORPUS + file_path
      ok = self.drive_manager.write_or_false(file_path, article.text)
      if not ok:
        log.warning("failed to write fyi text")

    if hasattr(article, 'markdown') and article.markdown:
      file_path = article.nav_key + '.md'
      file_path = self.drive_manager.config.DIR_CORPUS + file_path
      ok = self.drive_manager.write_or_false(file_path, article.markdown)
      if not ok:
        log.warning("failed to write markdown")

    return True

  def download(self, url: str, config: Optional[Config] = None,
               custom_headers: Optional[Dict[str, str]] = None
               ) -> Optional[Article]:
    """download article from url with retry logic"""
    if self._is_file_download(url):
      # todo: download the non-html file
      article = Article(url)
      article.download_exception_msg = 'mime err'
      return article

    headers = custom_headers or HTMLRequestHelper.get_request_headers()

    if not config:
      config = Config()
      config.request_timeout = self._timeout

    for attempt in range(self._max_retries + 1):
      try:
        if attempt > 1:
          headers = HTMLRequestHelper.get_request_headers_by_index(0)
        elif attempt > 0:
          headers = None

        config.headers = headers
        article = Article(url, config=config)
        article.download()

        if not self._validate_article_html(article):
          error = getattr(article, 'download_exception_msg', '')
          if '403' in error or '401' in error:
            article.download_exception_msg = f'forbidden: {error}'
          elif 'timeout' in error.lower():
            article.download_exception_msg = f'timeout: {error}'
          else:
            article.download_exception_msg = f'mystery: {error}'
          return article # hard wall

        time.sleep(self._sleep)
        article.download_exception_msg = ''
        log.info(f'successful download ({url}) [headers: {config.headers}]')
        return article

      except requests.exceptions.Timeout:
        article = Article(url)
        article.download_exception_msg = f'timeout (attempt {attempt + 1})'
        if attempt < self._max_retries:
          time.sleep(self._sleep * (attempt + 1))
          continue
        return article

      except Exception as e:
        article = Article(url)
        article.download_exception_msg = f'failure: {str(e)}'
        return article

    return article

  def load_from_file(self, key: Any) -> Optional[Article]:
    """load article from local or google drive html file"""
    if not key:
      log.warning('show me the key')
      return None

    if isinstance(key, int):
      key = f'{key:03d}'
      log.warning(f'key, numeric: {key}')

    if isinstance(key, str):
      try:
        nav_key = format_nav_path(key)
        file_path = nav_key + '.html'
        file_path = (Path(self.drive_manager.config.DIR_RAW) / file_path)
        file_path = self.drive_manager.config.resolve_path(str(file_path))
        log.warning(f'file_path: {file_path}')
        content = self.drive_manager.read(file_path)

        article = Article('')
        article.set_html(content)
        article.nav_key = nav_key
        return article
      except Exception as e:
        log.error(f"load from file '{file_path}' failed. {e}")

    return None

  def parse(self, article: Article) -> bool:
    """parse article content and extract metadata"""
    try:
      article.parse()
    except Exception as e:
      log.debug(f'newspaper3k parse failed: {e}')

    article.soup = BeautifulSoup(article.html, 'html.parser')

    config = self._entity_manager.get_entity(article.source_url)
    old_domain = article.source_url

    config = self._update_publisher_config(article, config)
    old_domain = ('' if article.source_url == old_domain 
                 else f"'{old_domain}' ↦ ")
    log.info(f"source_url: {old_domain}'{article.source_url}'")

    additional_data = self._extract_all_metadata(article, config)
    self._finalize_article_content(article, config, additional_data)

    try:
      file_path = (Path(self.drive_manager.config.DIR_CORPUS) / 
                   f'{article.nav_key}_imgs.txt')
      file_path = self.drive_manager.config.resolve_path(str(file_path))
      self.drive_manager.write(file_path, article.imgs)
    except Exception as e:
      log.info(f'error saving processed article: {e}')    

    self._update_markdown_images(article)

    return True

  def extract_nlp_features(self, article: Article) -> bool:
    """extract nlp features from parsed article"""
    if not article:
      log.error("no article")
      return False

    if not article.is_parsed:
      article.is_parsed = True
      log.warning("manually activated 'parsed' flag")

    article.nlp()

    # todo: override newspaper keywords
    # init: self.kw_yake = yake.KeywordExtractor(n=5,top=10)
    return True

  # metadata extraction methods
  def _extract_all_metadata(self, article: Article, 
                            config: Dict[str, Any]) -> Dict[str, Any]:
    """extract metadata from all configured sources"""
    additional_data = {}

    if article.source_url:
      publisher_name = self._publisher_manager.get_publisher_name(
        article.source_url)
      additional_data['publisher'] = publisher_name or ''

    additional_data.update(self._extract_article_metadata(article, config))

    nested_config = config.get('additional_data', [])
    if nested_config:
      additional_data.update(
        self._extract_article_metadata(article, nested_config))

    return additional_data

  def _extract_article_metadata(self, article: Article,
                                config: Dict[str, Any]) -> Dict[str, Any]:
    """extract metadata fields using configured selectors"""
    results = {}
    for field in self._article_fields:
      if field == 'images':
        pass # distinct but newspaper3k treats as alias for 'imgs'?
      elif field == 'imgs':
        img_tags = article.soup.find_all(['img','image'])
        if img_tags:
          img_data = {}
          for img in img_tags:
            alt = img.get('alt', '')
            src = img.get('src', '')
            if src and alt:
              img_data[src] = alt
          results[field] = json.dumps(img_data)
      elif field == 'meta_img':
        caption = article.soup.find('figcaption')
        results[field] = caption.get_text() if caption else ''
      else:
        field_config = config.get(field, [])
        if field_config:
          value = self._extract_field_value(article, field, field_config)
          if value:
            results[field] = self._process_field_value(field, value)
    return results

  def _extract_field_value(self, article: Article, field: str,
                           field_config: List[str]) -> Optional[Any]:
    """extract value using JSON-LD then CSS selectors"""
    json_ld_paths, css_selectors = self._classify_selectors(field_config)

    # try JSON-LD first
    for path in json_ld_paths:
      value = self._extract_from_json_ld(article, path)
      if value:
        return value

    if article.soup and css_selectors:
      return self._extract_with_css_selectors(article.soup, css_selectors)

    return None

  def _extract_from_json_ld(self, article: Article, 
                            field: str) -> Optional[List[Any]]:
    """extract field from json-ld schema data"""
    pattern = RegexConfig.JSON_LD
    matches = re.findall(pattern, article.html, re.DOTALL)

    for match in matches:
      try:
        data = json.loads(match)

        for key in field.split('.'):
          if isinstance(data, list):
            found = False
            for item in data:
              if isinstance(item, dict) and key in item:
                data = item.get(key, '')
                found = True
                break
            if not found:
              break
          elif isinstance(data, dict):
            if key in data:
              data = data[key]
            else:
              break

        if isinstance(data, list):
          log.info(f'{field} found: {data}')
          return data
        elif isinstance(data, str):
          log.info(f'{field} found: {data}')
          return self._normalize_to_list(data)

      except json.JSONDecodeError:
        continue

    return None

  def _extract_with_css_selectors(self, soup: BeautifulSoup,
                                  field_config: Dict[str, Any]
                                  ) -> Optional[Any]:
    """extract field using css selectors with domain-specific config"""
    if isinstance(field_config, dict):
      return self._combine_selector_content(soup, field_config)
    else:
      return self._extract_first_match(soup, field_config)

  def _extract_first_match(self, soup: BeautifulSoup, 
                           selectors: List[str]) -> Optional[str]:
    """extract content from first matching CSS selector"""
    for selector in selectors:
      element = soup.select_one(selector)
      if element:
        if element.name == 'meta':
          content = element.get('content')
        elif element.name == 'link':
          content = element.get('href')
        else:
          content = element.get_text()

        if content:
          return content.replace('\n', ' ').strip()
    return None

  def _combine_selector_content(self, soup: BeautifulSoup,
                                field_config: Dict[str, Any]
                                ) -> Optional[List[str]]:
    """extract and combine content from multiple CSS selectors"""
    actions = field_config.get('actions', [])
    selectors = field_config.get('selectors', [])
    stop_words = field_config.get('stops', [])
    delimiters = field_config.get('delimiters', [])

    combine = actions and actions[0] not in ['first']

    if not combine:
      return self._extract_first_match(soup, selectors)

    results = self._collect_selector_content(soup, selectors)
    if not results:
      return []

    processed_items = self._split_by_delimiters(results, delimiters)

    stop_words = ((stop_words or []) + (self._stop_words or []))
    filtered_results = self._filter_keywords(
      processed_items, truncate=False, stop_words=stop_words)

    return (sorted(set(filtered_results), key=str.lower)
            if filtered_results else [])

  def _collect_selector_content(self, soup: BeautifulSoup,
                                selectors: List[str]) -> List[str]:
    """collect content from all matching CSS selectors"""
    results = []
    for selector in selectors:
      element = soup.select_one(selector)
      if element:
        content = (element.get('content') if element.name == 'meta'
                  else element.get_text())
        if content:
          results.append(content.strip())
    return results

  # content processing methods
  def _extract_content_as_markdown(self, article: Article,
                                   config: Dict[str, Any]) -> str:
    """extract article content and convert to markdown"""
    if not article.html:
      log.warning('article has no html.')
      return ''

    tags = config.get('tags', [])
    body_html = self._extract_content_html(tags, article.html) or article.html

    if not body_html:
      log.warning('could not extract content from article html.')
      return ''
    else:
      try:
        file_path = (Path(self.drive_manager.config.DIR_CORPUS) / 
                     f'{article.nav_key}_premarkdown.txt')
        file_path = self.drive_manager.config.resolve_path(str(file_path))
        self.drive_manager.write(file_path, body_html)
      except Exception as e:
        log.info(f'error saving processed article: {e}')

      article.html = body_html

    return self._process_markdown(article, config)

  def _extract_content_html(self, tags: List[str], content: str) -> str:
    """extract html content using tag pairs"""
    if len(tags) < 2:
      log.warning("need at least one pair of open and close 'content:tags'")
      return ''

    matches = []
    for i, (open_tag, close_tag) in enumerate(zip(tags[::2], tags[1::2])):
      open_pattern = self._build_regex_pattern(open_tag)
      close_pattern = self._build_regex_pattern(close_tag)
      pattern = f'{open_pattern}(.*?){close_pattern}'

      matches = re.findall(pattern, content, re.DOTALL)
      if len(matches) == 1:
        log.info(f'length = {len(matches[0])} ↤ {len(content)} with body '
                 f'pattern [{repr(pattern)}].')
        break
      log.warning(f'pair {i} has {len(matches)} matches; trying next pair')

    if not matches:
      log.warning('no content tag pairs had matches. check configuration.')
      return ''

    return matches[0]

  def _extract_content_markdown(self, pattern: str, 
                                html: str) -> Optional[List[str]]:
    """extract HTML content using tag pairs"""
    if not pattern:
      log.warning('missing pattern to search markdown with')
      return []

    return re.findall(pattern, html, re.DOTALL)

  def _process_markdown(self, article: Article, 
                        config: Dict[str, Any]) -> str:
    """convert html to markdown with html fallback"""
    original_length = len(article.html)
    markdown = self._html_converter.handle(article.html)
    log.info(f'length: {len(markdown)} ↤ {original_length} with '
            f'html2text.handle')

    original_length = len(markdown)
    markdown = markdown.replace('\r\n', '\n').replace('\r', '\n')
    log.info(f'length: {len(markdown)} ↤ {original_length} with '
            f'normalized \n')

    markdown = self._apply_markdown_edits(markdown, config)

    header = self._generate_header(article) or ''
    markdown = header + markdown

    return re.sub(r'\n{3,}', '\n\n', markdown)

  def _apply_markdown_edits(self, markdown: str,
                            config: Dict[str, Any]) -> str:
    """apply edits to markdown"""
    try:
      edits = config.get('md_edits', [])
      for i, edit in enumerate(edits):
        original_length = len(markdown)
        find_pattern = edit.get('find', '')
        if find_pattern:
          pattern = self._build_regex_pattern(find_pattern)

          replacement = edit.get('repl', '')
          if replacement:
            replacement = self._build_regex_pattern(replacement)

          scope = edit.get('scope', '')
          try:
            if scope:
              scope_pattern = self._build_regex_pattern(scope)
              scopes = (self._extract_content_markdown(scope_pattern,
                                                      markdown) or [markdown])
              for content_scope in scopes:
                scoped = re.sub(pattern, replacement, content_scope,
                               flags=re.DOTALL)
                markdown = markdown.replace(content_scope, scoped)
            else:
              markdown = re.sub(pattern, replacement, markdown,
                               flags=re.DOTALL)
          except Exception as e:
            log.warning(e)

          log.info(f'#{i} length: {len(markdown)} ↤ {original_length} '
                   f'with edit pattern [{repr(pattern)}]')

      return markdown
    except Exception as e:
      log.warning(e)
    return markdown

  def _finalize_article_content(self, article: Article, 
                                config: Dict[str, Any],
                                additional_data: Dict[str, Any]) -> None:
    """update article attributes and extract content"""
    additional_data = self._update_attributes(article, additional_data)
    article.additional_data = json.dumps(additional_data)

    content = self._extract_content_as_markdown(
      article, config.get('content', []))
    article.text = (convert_markdown_to_text(content) or article.text)

    yaml_header = self._generate_yaml_header(article) or ''
    article.markdown = yaml_header + content

  # data processing helpers
  def _process_field_value(self, field: str, value: Any) -> Any:
    """apply field-specific transformations"""
    if field == 'authors' and isinstance(value, str):
      return value.replace('By ', '')
    return value

  def _filter_keywords(self, keywords: Any, truncate: bool = True,
                       stop_words: Optional[List[str]] = None) -> List[str]:
    """clean keywords: truncate from first stop word else filter all"""
    stop_words = stop_words or self._stop_words

    if not keywords:
      return []

    if isinstance(keywords, list):
      return self._filter_keyword_list(keywords, truncate, stop_words)
    elif isinstance(keywords, str):
      return self._filter_keyword_string(keywords, truncate, stop_words)
    else:
      return self._filter_single_keyword(keywords, truncate, stop_words)

  def _filter_keyword_list(self, keywords: List[Any], truncate: bool,
                           stop_words: List[str]) -> List[str]:
    """filter list of keywords, optionally truncating at first stop word"""
    filtered = []
    for item in keywords:
      item_str = str(item).strip()
      if not item_str:
        continue

      if not self._has_stop_word(item_str, stop_words):
        filtered.append(item_str)
      elif truncate:
        break
    return filtered

  def _filter_keyword_string(self, keywords: str, truncate: bool,
                             stop_words: List[str]) -> List[str]:
    """filter comma-separated keyword string"""
    delimiter = ","

    if truncate:
      keywords = self._truncate_at_stop_word(keywords, delimiter, stop_words)

    parts = [k.strip() for k in keywords.split(delimiter) if k.strip()]

    if truncate:
      return parts
    else:
      return [k for k in parts if not self._has_stop_word(k, stop_words)]

  def _filter_single_keyword(self, keyword: Any, truncate: bool,
                             stop_words: List[str]) -> List[str]:
    """filter single keyword value"""
    single_keyword = str(keyword).strip()
    if not single_keyword:
      return []
  
    should_include = (truncate or 
                     not self._has_stop_word(single_keyword, stop_words))
    return [single_keyword] if should_include else []

  def _truncate_at_stop_word(self, keywords: str, delimiter: str,
                             stop_words: List[str]) -> str:
    """truncate keyword string at first stop word occurrence"""
    keywords_lower = keywords.lower()
    earliest_idx = len(keywords)

    for stop_word in stop_words:
      idx = keywords_lower.find(f'{delimiter} {stop_word}')
      if idx >= 0:
        earliest_idx = min(earliest_idx, idx)

    if earliest_idx < len(keywords):
      keywords = keywords[:earliest_idx]

    return keywords

  def _split_by_delimiters(self, content_list: List[str],
                           delimiters: Optional[List[str]]) -> List[str]:
    """split content by multiple delimiters sequentially"""
    if not delimiters:
      return content_list

    delimiter = delimiters[0] if delimiters else ','

    combined_text = f'{delimiter} '.join(content_list)
    current_items = [item.strip() for item
                    in combined_text.split(delimiter) if item.strip()]

    for sub_delimiter in delimiters[1:]:
      next_items = []
      for item in current_items:
        if sub_delimiter in item:
          sub_items = [k.strip() for k
                      in item.split(sub_delimiter) if k.strip()]
          next_items.extend(sub_items)
        else:
          next_items.append(item)
      current_items = next_items

    return current_items

  def _normalize_to_list(self, value: Any) -> List[Any]:
    """convert various types to consistent list format"""
    if isinstance(value, list):
      return value
    elif isinstance(value, str):
      return [k.strip() for k in value.split(',')]
    else:
      return [value]

  def _update_attributes(self, article: Article, 
                         updates: Dict[str, Any]) -> Dict[str, Any]:
    """update article attributes from dictionary, returning unused keys"""
    valid_keys = [k for k in updates if not k.startswith('_') and
                 (not self._article_fields or k in self._article_fields)]

    for key in valid_keys:
      try:
        log.info(f'{key} ↦ {updates[key]}')
        value = updates.pop(key)
        if isinstance(value, list):
          value = ', '.join(value)
        setattr(article, key, value)
      except (AttributeError, TypeError) as e:
        log.warning(f'failed to set {key}: {e}')

    return updates

  # image processing helpers
  def _find_matching_img_src(self, filename: str,
                             img_dict: Dict[str, str]) -> Optional[str]:
    """find img src that contains the given filename"""
    for src_key in img_dict:
      if filename in src_key:
        return src_key
    return None

  def _should_replace_alt_text(self, alt_text: str) -> bool:
    """check if alt text should be replaced"""
    return not alt_text or 'http' in alt_text

  def _update_markdown_images(self, article: Article) -> bool:
    """update markdown image alt text with data from img tags"""
    if article.imgs:
      img_dict = json.loads(article.imgs)

      def replace_match(match):
        alt_text = match.group(1)
        url = match.group(2)
        filename = os.path.basename(url.split('?')[0])

        if self._should_replace_alt_text(alt_text):
          matching_key = self._find_matching_img_src(filename, img_dict)
          new_alt = img_dict.get(matching_key, '') if matching_key else ''
          return f'![{new_alt}]({url})'

        return match.group(0)

      article.markdown = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_match, article.markdown)

      # if load vs download
      key = article.nav_key.split('/')[-1]
      article.markdown = article.markdown.replace('](images/',f'](images/{key}_')
    return True

  # validation and classification helpers
  def _classify_selectors(self, selectors: List[str]
                          ) -> Tuple[List[str], List[str]]:
    """separate JSON-LD paths from CSS selectors"""
    json_ld_paths = []
    css_selectors = []

    for selector in selectors:
      if self._is_json_ld_path(selector):
        json_ld_paths.append(selector)
      else:
        css_selectors.append(selector)

    return json_ld_paths, css_selectors

  def _is_json_ld_path(self, selector: str) -> bool:
    """detect JSON-LD path vs CSS selector"""
    return ('.' in selector and
            not any(selector.startswith(prefix) for prefix
                   in self._CSS_PREFIXES) and
            not selector.startswith(('div.', 'span.')))

  def _is_file_download(self, url: str) -> bool:
    """check if URL points to file vs HTML"""
    mime_type, _ = mimetypes.guess_type(url)
    if mime_type is None:
      return False
    return not mime_type.startswith(('text/html', 'application/xhtml+xml'))

  def _validate_article_html(self, article: Article) -> bool:
    """validate article contains HTML"""
    if not article or not hasattr(article, 'html') or not article.html:
      return False

    if hasattr(article, 'response') and article.response:
      content_type = article.response.headers.get('content-type', '').lower()
      if self._is_file_download(content_type):
        return False

      content_disposition = article.response.headers.get(
        'content-disposition', '')
      if 'attachment' in content_disposition.lower():
        return False

    if article.html.count('\x00') > len(article.html) * 0.01:
      return False

    return True

  def _has_stop_word(self, text: str,
                     stop_words: Optional[List[str]] = None) -> bool:
    """check if text contains any stop word (partial matching)"""
    stop_words = stop_words or self._stop_words
    text_lower = text.lower()
    return any(word.lower() in text_lower for word in stop_words)

  # formatting and generation helpers
  def _build_regex_pattern(self, pattern: str) -> Optional[str]:
    """build regex pattern from configuration string"""
    if not pattern:
      return ''

    if pattern.find(RegexConfig.FLAG) < 0:
      return (re.escape(pattern)
              .replace(r'\*', RegexConfig.WILDCARD)
              .replace(r'\/', '/'))

    return pattern.replace(RegexConfig.FLAG, '')

  def _generate_header(self, article: Article) -> str:
    """generate markdown header for article"""
    if re.search(RegexConfig.HEADLINE, article.text, re.MULTILINE):
      return ''

    header = f'# {article.title}\n'
    if article.meta_description:
      header += f'\n{article.meta_description}\n'
    if article.top_image:
      header += f'\n![{article.meta_img or ""}]({article.top_image})\n'
    if article.meta_img:
      header += f'\n{article.meta_img}\n'
    if article.authors:
      header += f'\nBy {article.authors}\n'
    if article.publish_date:
      header += f'\nPublished {article.publish_date}\n'
    header += '\n'

    return header

  def _generate_yaml_header(self, article: Article) -> str:
    """generate YAML frontmatter header"""
    fields = {
      'title': article.title or '',
      'description': article.meta_description or '',
      'canonical': article.canonical_link or article.url or '',
      'author': article.authors or '',
      'date': article.publish_date or '',
      'tags': article.keywords or '',
      'category': self._get_article_category(article)}

    yaml_content = '\n'.join(f'{k}: {v}' for k, v in fields.items())
    return f'---\n{yaml_content}\n---\n'

  def _get_article_category(self, article: Article) -> str:
    """get article category from publisher manager"""
    return self._publisher_manager.get_publisher_type(article.source_url)

  # configuration helpers
  def _update_publisher_config(self, article: Article,
                               default_config: Dict[str, Any]
                               ) -> Dict[str, Any]:
    """extract canonical URL and return publisher-specific configuration"""
    article.canonical_url = self._extract_with_css_selectors(
      article.soup, default_config.get('url', []))

    article.source_url = URLHelper.extract_domain(article.canonical_url)

    if not URLHelper.is_valid_url(article.url):
      article.url = article.canonical_url

    return self._entity_manager.get_entity(article.source_url)

  # setup methods
  def _setup_article_fields(self) -> None:
    """extract available article fields for metadata extraction"""
    sample_article = Article('')
    self._article_fields = [
      attr for attr in dir(sample_article)
      if not attr.startswith('_') and 
      not callable(getattr(sample_article, attr))]

  def _setup_html_converter(self) -> None:
    """configure HTML to markdown converter"""
    self._html_converter = html2text.HTML2Text()
    self._html_converter.ignore_links = False
    self._html_converter.body_width = 0
