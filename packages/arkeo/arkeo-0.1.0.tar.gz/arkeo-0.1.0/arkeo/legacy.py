import inspect
import logging
from dataclasses import asdict, dataclass, fields
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union

import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe
from pandas import DataFrame, Series
from newspaper import Article
from tqdm.notebook import tqdm

from article.loader import ArticleLoader
from publisher import PublisherManager
from utils.access import SheetsClientManager
from utils.text import AlphaNumHelper, expand_to_list


log = logging.getLogger(__name__)


class SheetStatus(Enum):
  """legacy processing status flags"""
  OK = 'OK'
  CHECK = 'ck'
  DELETE = 'd'
  DIY = 'diy'
  DLF = 'dlf'
  PAYWALL = '$'

  @classmethod
  def system_flags(cls) -> List['SheetStatus']:
    """flags managed by the system"""
    return [cls.OK.value, cls.CHECK.value, cls.DIY.value]

  @classmethod
  def user_flags(cls) -> List['SheetStatus']:
    """flags managed by users"""
    return [cls.DELETE.value, cls.DLF.value]

  @classmethod
  def all_flags(cls) -> List['SheetStatus']:
    """fll available flags"""
    return cls.system_flags() + cls.user_flags()


@dataclass
class MigrationData:
  loc: str = ""
  publisher: str = ""
  pubdt: str = ""
  headline: str = ""
  subtitle: str = ""
  url: str = ""
  arc: str = ""
  insby: str = ""
  updby: str = ""
  content: str = ""


@dataclass
class MigratedData:
  loc: str = ""  # double last known
  flag: str = ""
  url: str = ""
  pubdt: str = ""
  headline: str = ""
  subtitle: str = ""
  author: str = ""
  abstract: str = ""
  keywords: str = ""
  content: str = ""
  size: int = 0
  insby: str = ""  # double last known
  updby: str = ""  # double last known
  domain: str = ""
  publisher: str = ""
  fwd: str = ""
  arc: str = ""
  memo_int: str = ""
  meta_data: str = ""
  stg_info: str = ""


class ArticleLegacy:
  """handles batch processing and dataframe updates for single worksheet"""

  # Primary and unique keys
  PK = 'key'
  UK_ARC = 'arc'
  UK_FWD = 'fwd'
  UK_URL = 'url'

  # Article processor fields
  AP_STATUS = 'flag'
  AP_STATUS_MEMO = 'stg_info'
  AP_PUBLISHER = 'publisher'

  _MAP = {
    PK: 'ArticleLegacy._generate_key',
    AP_STATUS: 'ArticleLegacy._get_status',
    UK_URL: 'Article.canonical_url',
    'pubdt': 'Article.publish_date',
    'headline': 'Article.title',
    'subtitle': 'Article.meta_description',
    'author': 'Article.authors',
    'abstract': 'Article.summary',
    'keywords': 'Article.meta_keywords',
    'content': 'Article.text',
    'size': 'ArticleLegacy._get_text_length',
    'ins_by': 'ArticleLegacy._generate_ins_by',
    'upd_by': 'ArticleLegacy.upd_by',
    'nav_key': 'ArticleLegacy._generate_nav_key',
    'domain': 'Article.source_url',
    AP_PUBLISHER: 'ArticleLegacy._get_publisher',
    UK_FWD: 'ArticleLegacy._get_forward_url',
    UK_ARC: 'ArticleLegacy._get_archive_url',
    'meta_data': 'ArticleLegacy._get_meta_data',
    AP_STATUS_MEMO: 'ArticleLegacy._get_status_info'
  }

  _REGEX_NA_PANDAS = r'^\s*$'

  def __init__(self,
               loader: Optional[ArticleLoader] = None):
    self._user = 'bot'
    self._worksheet = None
    self.loader = loader

    self.df = self._get_dataframe()

  @property
  def worksheet(self) -> gspread.Worksheet:
    """lazy load worksheet connection"""
    if self._worksheet is None:
      try:
        client = SheetsClientManager.get_client()
        spreadsheet = client.open('fsi')
        self._worksheet = spreadsheet.worksheet('data')
      except Exception as e:
        log.error(f'failed to connect to worksheet: {str(e)}')
        raise

    return self._worksheet

  @property
  def upd_by(self) -> str:
    return self._user

  # main
  def file_some(self, keys: Union[str, List[str]] = None):
    """bridge gaps in markdown/text files"""
    if self.df is None:
      log.error('dataframe not loaded')
      return

    try:
      filtered_rows = self._get_filtered_rows_by_status(
        keys, SheetStatus.all_flags())
      
      for key in tqdm(filtered_rows[self.PK],
                      desc="processing articles",
                      ncols=80, ascii=True):
        try:
          mask = self.df[self.PK] == key
          self.file_one(mask)
        except Exception as e:
          log.error(f'error exporting files, key {key}: {e}')
          continue

    except Exception as e:
      log.error(e)
      raise

  def file_one(self, mask: Series):
    """output markdown or text files"""
    base_path = self.loader.drive_manager.config.DIR_CORPUS
    nav_key = self.df.loc[mask, 'nav_key'].item()
    
    try:
      file_dir = base_path + self.loader._format_nav_path(nav_key)
      file_dir = self.loader.drive_manager.config.resolve_path(file_dir)
      
      # check for existing files
      for ext, desc in [('.md', 'markdown'), ('.txt', 'text file')]:
        file_path = file_dir + ext
        if self.loader.drive_manager.file_exists(file_path):
          log.info(f'[{nav_key}]: {desc} exists')
          return
      
      # write new text file
      text = self.df.loc[mask, 'content'].item()
      file_path = file_dir + '.txt'
      if self.loader.drive_manager.write_or_false(file_path, text):
        log.info(f'[{nav_key}]: text file written')
      else:
        log.info(f'[{nav_key}]: failed to output file')
        
    except Exception as e:
      log.warning(f'[{nav_key}]: {e}!!')

  def update_articles(self, keys: Union[str, List[str]] = None,
                       override: bool = False) -> None:
    """process articles and update dataframe"""
    if self.df is None:
      log.error('dataframe not loaded')
      return

    try:
      filtered_rows = self._get_filtered_rows_by_status(
        keys, [] if override else SheetStatus.all_flags())
      
      for key in tqdm(filtered_rows[self.PK],
                      desc="processing articles",
                      ncols=80, ascii=True):
        try:
          mask = self.df[self.PK] == key
          self._update_article_row(mask, download=True)
        except Exception as e:
          log.error(f'error downloading urls, key {key}: {e}')
          continue

      self._save_dataframe()
    except Exception as e:
      log.error(e)
      raise

  def update_articles_downloaded(self, keys: Union[str, List[str]] = None,
                                  override: bool = False) -> None:
    """process already downloaded articles and update dataframe"""
    if self.df is None:
      log.error('dataframe not loaded')
      return

    try:
      filtered_rows = self._get_filtered_rows_by_status(
        keys, [] if override else SheetStatus.DLF)

      for key in tqdm(filtered_rows[self.PK],
                      desc="processing articles",
                      ncols=80, ascii=True):
        try:
          mask = self.df[self.PK] == key
          self._update_article_row(mask)
        except Exception as e:
          log.error(f'error importing files, key {key}: {e}')
          continue

      self._save_dataframe()
    except Exception as e:
      log.error(e)
      raise

  def migrate_rows(self, ids: List[int] = None,
                   old_nm: str = 'fsi', user: str = 'fsi'):
    old_worksheet = SheetsClientManager.open_sheet(old_nm).get_worksheet(0)
    df = get_as_dataframe(old_worksheet, parse_dates=True, header=2)
    df = df.infer_objects(copy=False).fillna('')

    # select columns [1-3,6-11] ~> [0-2,5-10]
    desired_columns = list(range(0, 3)) + list(range(5, 11))
    df = df.iloc[:, desired_columns]

    # extract field names from MigrationData dataclass
    new_headers = [field.name for field in fields(MigrationData)]
    df.columns = new_headers[:len(df.columns)]

    # filter by url existence, column 7 ~> index 4
    df = df[df.iloc[:, 4].notna() & (df.iloc[:, 4] != '')]
    if ids:
      df = df[df['loc'].isin(ids)]
    df = df.reset_index(drop=True)

    # convert to list of dicts once, then iterate
    records = df.to_dict('records')
    for record in tqdm(records, desc="migrating rows"):
        migration_data = MigrationData(**record)
        self.migrate_row(migration_data, user)

    self.save_migrated()

  def migrate_row(self, migration_data: MigrationData,
                  user: str = None) -> bool:
    """
    add/update article row to new sheet as migration from old sheet.

    args:
      migration_data: MigrationData instance to migrate

    returns:
      True if successfully added else False (surprise!)
    """
    if self.df is None:
      self._load_dataframe()

    if not migration_data or not migration_data.loc:
      return False

    try:
      loc = int(migration_data.loc) # int() wth!!
      url = migration_data.url or ''
      domain = self.loader.pubmgr.extract_domain(url)
      publisher_name = getattr(migration_data,'publisher','')
      pub_type = ''

      if domain and (publisher := self.loader.pubmgr.get_publisher(domain)):
        publisher_name = publisher.name or publisher_name # SIGH
        pub_type = publisher.category or ''

      pubdt = migration_data.pubdt or None

      row_mask = self.df['loc'] == loc
      row_exists = not self.df[row_mask].empty

      content = str(migration_data.content or '') # str() wth!!
      size = len(content)
      flag = self._get_migration_flag(size, pub_type)

      insby = migration_data.insby or ''
      updby = migration_data.updby or ''
      processed_insby = (insby + (';' + updby if updby else '')).replace(' ','')

      if row_exists:
        self.df.loc[row_mask,'flag'] = flag
        self.df.loc[row_mask,'url'] = url
        self.df.loc[row_mask,'publisher'] = publisher_name
        self.df.loc[row_mask,'pubdt'] = pubdt
        self.df.loc[row_mask,'headline'] = migration_data.headline or ''
        self.df.loc[row_mask,'content'] = content
        self.df.loc[row_mask,'size'] = size
        self.df.loc[row_mask,'arc'] = migration_data.arc or ''
        self.df.loc[row_mask,'insby'] = processed_insby
        self.df.loc[row_mask,'updby'] = user or self._user
        self.df.loc[row_mask,'domain'] = domain

        print(f'updated migration data: [{int(loc):03d}] {url}')
        return True

      else:

        migrated_data = MigratedData(
          loc = loc,
          flag = flag,
          url = url,
          publisher = publisher_name,
          pubdt = pubdt,
          headline = migration_data.headline or '',
          content = content,
          size = size,
          insby = processed_insby,
          updby = 'bot',
          domain = domain,
          arc = migration_data.arc or '' )
        new_row_data = asdict(migrated_data)

        # get column order from dataclass
        cols = [field.name for field in fields(MigratedData)]
        new_row = [new_row_data.get(col,'') for col in cols]

        # append to google worksheet
        #self.worksheet.append_row(new_row) # do as bulk action with any udpates

        # update local dataframe with all colums (including calculated ones as empty)
        new_df_row = pd.DataFrame([new_row_data])
        self.df = pd.concat([self.df,new_df_row],ignore_index=True)

        print(f'inserted migration data: [{int(loc):03d}] {url}')
        return True
    except Exception as e:
      print(f'error processing migration data {migration_data.loc}: {e}')
      return False

  # helpers, load
  def _get_dataframe(self) -> Optional[DataFrame]:
    """load dataframe from google sheets"""
    try:
      df = get_as_dataframe(self.worksheet, evaluate_formulas = True)
      # modify for google sheets x pandas
      df[self.PK] = df[self.PK].astype(str).str.zfill(3)  # alphanumeric pk
      return df.fillna('')
    except Exception as e:
      log.error(f'failed to load dataframe: {str(e)}')
      return None

  def _get_filtered_rows_by_status(self, keys: Union[str, List[str]], 
                                   status: Union[str, List[str]]) -> DataFrame:
    """get filtered rows based on keys and override settings"""
    expanded_keys = expand_to_list(keys)

    if expanded_keys:
      filtered_rows = self.df[self.df[self.PK].isin(expanded_keys)]
    else:
      filtered_rows = self.df

    if status:
      if isinstance(status, str):
        status = [status]
      return filtered_rows[filtered_rows[self.AP_STATUS].isin(status)]

    return filtered_rows

  # helpers, update
  def _update_article_row(self, mask: Series, download: bool = False) -> None:
    """process a single article row"""
    key = self.df.loc[mask, self.PK]
    url = self.df.loc[mask, self.UK_URL]

    try:
      if download:
        article = self.loader.download(url)
      else:
        article = self.loader.load_from_file(key)
        if article and url:
          article.url = url

      self._update_row(mask, article)
      status = self._extract_status_code(article)
      log.info(f'{key} [{status}]: {url} '
               f'{getattr(article, "download_exception_msg", "")}')
    except Exception as e:
      log.error(f'failed to process article {key}: {str(e)}')
      self.df.loc[mask, self.AP_STATUS_MEMO] = f'error: {str(e)[:50]}'

  def _update_row(self, mask: Series, article: Article) -> None:
    """update entire row with article data"""
    if self.df is None:
      log.error('dataframe not loaded')
      return

    if not article:
      self.df.loc[mask, self.AP_STATUS_MEMO] = 'unloaded'
      return

    for target_col, source_ref in self._MAP.items():
      try:
        value = self._get_mapped_value(source_ref, mask, article)
        if value is not None:
          self._update_cell_if_changed(mask, target_col, value)
      except Exception as e:
        log.warning(f'error processing map[{target_col}]: {str(e)}')

  def _get_mapped_value(self, source_ref: str, mask: Series, 
                        article: 'Article') -> Any:
    """get value from mapped source reference"""
    try:
      source_class, source_attr = source_ref.split('.')

      if source_class == 'Article':
        return getattr(article, source_attr, '')

      elif source_class == 'ArticleLegacy':
        method = getattr(self, source_attr)

        if source_attr.startswith('_'):
          sig = inspect.signature(method)
          if len(sig.parameters) == 3:  # self, mask, article
            return method(mask, article)
          else:  # self, article
            return method(article)
        else:  # property
          return method

      else:
        log.warning(f'invalid class in mapping: {source_class}')
        return None

    except (AttributeError, ValueError) as e:
      log.warning(f'invalid mapping reference {source_ref}: {str(e)}')
      return None

  def _update_cell_if_changed(self, mask: Series, target_col: str, 
                              value: Any) -> None:
    """update cell only if value has changed"""
    try:
      # format value based on type
      if isinstance(value, list):
        formatted_value = ', '.join(map(str, value))
      elif isinstance(value, datetime):
        formatted_value = value.strftime('%Y-%m-%d')
      elif hasattr(value, 'strftime'):  # date object
        formatted_value = value.strftime('%Y-%m-%d')
      else:
        formatted_value = str(value) if value is not None else ''

      # only update if value changed
      current_value = self.df.loc[mask, target_col].iloc[0]
      if current_value != formatted_value:
        self.df.loc[mask, target_col] = formatted_value

    except Exception as e:
      log.warning(f'error updating {target_col}: {str(e)}')

  def _extract_status_code(self, article: 'Article') -> str:
    """get display status for processing logs"""
    if not article:
      return 'no_article'

    if hasattr(article, 'download_exception_msg') and \
       article.download_exception_msg:
      return article.download_exception_msg[:8]

    text_length = len(getattr(article, 'text', ''))
    return f'# {text_length:06d}'

  def _save_dataframe(self) -> None:
    """save dataframe back to google sheets"""
    if self.df is None:
      log.warning('no dataframe to save')
      return

    try:
      cleaned_df = self.df.fillna('').replace(
        self._REGEX_NA_PANDAS, '', regex=True)

      data = [cleaned_df.columns.values.tolist()] + \
             cleaned_df.values.tolist()

      self.worksheet.update(data)
      log.info('successfully saved dataframe to sheets')
    except Exception as e:
      log.error(f'failed to save dataframe: {str(e)}')
      raise

  def _save_migrated(self) -> None:
    """write dataframe to google sheets"""
    cols = [field.name for field in fields(MigratedData)]

    # clean the dataframe first
    df_clean = self.df.fillna('').replace(r'^\s*$', '', regex=True)

    # convert cleaned dataframe to data rows
    data_rows = []
    for _, row in df_clean.iterrows():
      row_values = [str(row.get(col, '')) for col in cols]
      data_rows.append(row_values)

    # write current dataframe data
    if data_rows:
      self.worksheet.update(range_name="A2",values=data_rows)

    print(f'synced {len(df_clean)} rows to google sheets')

  def _get_migration_flag(self, text_size: int, pub_type: str) -> str:
    if text_size < 1000 or pub_type in(PublisherManager.PUB_TYPES_DIY):
      return SheetStatus.DIY.value
    else:
      return SheetStatus.OK.value

  # mapped attribute updates
  def _get_archive_url(self, article: Article) -> Optional[str]:
    """get archive url from article additional info"""
    if not article or not hasattr(article, 'additional_info') or \
       not article.additional_info:
      return None

    archive_url = article.additional_info.get(self.UK_ARC, '')
    return archive_url if archive_url else None

  def _get_forward_url(self, article: Article) -> Optional[str]:
    """get forward url from article additional info or detect redirect"""
    if not article:
      return None

    if hasattr(article, 'additional_info') and article.additional_info:
      forward_url = article.additional_info.get(self.UK_FWD, '')
      if forward_url:
        return forward_url

    # detect if url was redirected
    if hasattr(article, 'url') and hasattr(article, 'canonical_url') and \
       article.url != article.canonical_url:
      return article.url

    return None

  def _generate_ins_by(self, mask: Series, article: Article) -> str:
    """generate or preserve ins_by field"""
    try:
      ins_by = self.df.loc[mask, 'ins_by'].iloc[0]
      return ins_by if ins_by else self._user
    except (IndexError, KeyError):
      return self._user

  def _generate_key(self, mask: Series, article: Article) -> Optional[str]:
    """generate new key if not exists"""
    try:
      current_key = self.df.loc[mask, self.PK].iloc[0]
      if not current_key:
        max_key = self.df[self.PK].max()
        return AlphaNumHelper.increment(max_key)
      return current_key
    except Exception as e:
      log.warning(f'error generating key: {str(e)}')
      return None

  def _get_meta_data(self, article: Article) -> str:
    """get article metadata as string"""
    # TODO: implement based on requirements but pandas
    return ''

  def _generate_nav_key(self, mask: Series, 
                        article: 'Article') -> Optional[str]:
    """generate navigation key from date and primary key"""
    try:
      key = self.df.loc[mask, self.PK].iloc[0]
      if not key:
        log.warning('set primary key "key" first')
        return None

      if article and hasattr(article, 'publish_date') and \
         article.publish_date:
        article_date = article.publish_date
      else:
        article_date = date.today()

      # convert to datetime if needed
      if hasattr(article_date, 'strftime'):
        date_str = article_date.strftime('%Y-%m')
      else:
        date_str = datetime.now().strftime('%Y-%m')

      return f'{date_str}-{key}'
    except Exception as e:
      log.warning(f'error generating nav_key: {str(e)}')
      return None

  def _get_publisher(self, article: Article) -> str:
    """get publisher name from article or url"""
    if not article:
      return ''

    # check additional info first
    if hasattr(article, 'additional_info') and article.additional_info:
      publisher = article.additional_info.get(self.AP_PUBLISHER, '')
      if publisher:
        return publisher

    # fallback to publisher manager
    if hasattr(article, 'source_url') and article.source_url:
      try:
        return self.loader.pubmgr.get_publisher_name(article.source_url)
      except Exception as e:
        log.warning(f'error getting publisher: {str(e)}')

    return ''

  def _get_status(self, article: 'Article') -> str:
    """determine article processing status based on content"""
    if not article or not hasattr(article, 'text'):
      return ''

    text_size = len(article.text)

    if text_size > 1000:
      return SheetStatus.OK.value
    elif text_size > 200:
      return SheetStatus.CHECK.value
    elif text_size == 0:
      try:
        if hasattr(article, 'source_url') and article.source_url:
          publisher_type = self.loader.pubmgr.get_publisher_type(
            article.source_url)
          if publisher_type in self.loader.pubmgr.PUB_TYPES_DIY:
            return SheetStatus.DIY.value
      except Exception as e:
        log.warning(f'error checking publisher type: {str(e)}')

    return ''

  def _get_status_info(self, article: 'Article') -> str:
    """get detailed status information"""
    if not article:
      return 'no article'

    if hasattr(article, 'download_exception_msg') and \
       article.download_exception_msg:
      return article.download_exception_msg

    return f'processed: {len(getattr(article, "text", ""))} chars'

  def _get_text_length(self, article: 'Article') -> int:
    """get article text length"""
    if article and hasattr(article, 'text') and article.text:
      return len(article.text)
    return 0