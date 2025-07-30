import re
from dataclasses import dataclass

from newspaper import Article


@dataclass(frozen=True)
class MarkdownPatterns:
  """Regex patterns for markdown to text conversion"""
  YAML: str = r'^---\n.*?\n---'
  HEADERS: str = r'^#{1,6}\s+'
  BOLD: str = r'\*{1,2}([^*]+)\*{1,2}'
  ITALIC: str = r'_{1,2}([^_]+)_{1,2}'
  LINKS: str = r'\[([^\]]+)\]\([^)]+\)'
  CODE_BLOCKS_1: str = r'```[^`]*```'
  CODE_BLOCKS_2: str = r'`([^`]+)`'
  WHITESPACE: str = r'\n\s*\n'


def is_nav_key_format(s):
  """YYYY-mm-ZZZ"""
  return (isinstance(s, str) and 
          len(s) == 11 and 
          s[4] == '-' and 
          s[7] == '-' and
          s[:4].isdigit() and
          s[5:7].isdigit() and
          s[8:].isalnum() and
          s[8:].isupper())

def convert_markdown_to_text(text: str) -> str:
  """convert markdown to plain text"""
  text = re.sub(MarkdownPatterns.YAML, '', text, 1, flags=re.DOTALL)
  text = re.sub(MarkdownPatterns.HEADERS, '', text, 1, flags=re.DOTALL)
  text = re.sub(MarkdownPatterns.BOLD, r'\1', text)
  text = re.sub(MarkdownPatterns.ITALIC, r'\1', text)
  text = re.sub(MarkdownPatterns.LINKS, r'\1', text)
  text = re.sub(MarkdownPatterns.CODE_BLOCKS_1, '', text, flags=re.DOTALL)
  text = re.sub(MarkdownPatterns.CODE_BLOCKS_2, r'\1', text)
  text = re.sub(MarkdownPatterns.WHITESPACE, '\n\n', text)
  return text.strip()


def format_nav_path(nav_key: str) -> str:
  """format navigation path: yyyy-mm-zzz → yyyy/mm/zzz"""
  return nav_key.replace('-', '/')


def to_str(article: Article, prove_its_useless: bool = True,
           shorter: bool = True) -> str:
  """convert article to formatted string representation
  
  args:
    prove_its_useless: if display potentially unused attributes
    shorter: if exclude verbose content fields
  """
  rc = ""

  attrs = [
    (article.url, "url", "", ""),
    (article.title, "headline", "", ""),
    (article.publish_date, "published", "", ""),
    (article.top_image, "top image", "", ""),
    (article.movies, "videos", "", ""),
    (article.summary, "abstract (nlp)", "", "\n\n"),
    (article.keywords, "keywords (nlp)", "", ""),
    (article.additional_data, "additional_data", "", ""),
    (article.canonical_link, "canonical_link", "", ""),
    (article.download_exception_msg, "download_exception_msg", "", ""),
    (article.meta_description, "meta_description", "", ""),
    (article.meta_img, "meta_img", "", ""),
    (article.meta_keywords, "meta_keywords", "", ""),
    (article.source_url, "source_url", "", "")]

  if prove_its_useless:
    attrs.extend([
      (article.authors, "authors", "*", ""),
      (article.download_state, "download_state", "*", ""),
      (article.images, "images", "*", ""),
      (article.imgs, "imgs", "*", ""),
      (article.tags, "tags", "*", ""),
      (article.top_img, "top_img", "*", "")])

  if not shorter:
    attrs.extend([
      (article.text, "content", "", "\n\n"),
      (article.meta_data, "meta_data", "", "")])

  ws = max(len(attr[1]) for attr in attrs)
  for attr in attrs:
    padding = " " * (ws - len(attr[1]))
    marker = attr[2] or " "
    rc += f"\n{padding}{attr[1]}{marker}:  {attr[3]}{str(attr[0])}"

  return rc