import logging
import random
import re
from typing import Dict, Generator, List, Optional, Union
from urllib.parse import urlparse

import tldextract


log = logging.getLogger(__name__)


def expand_to_list(range_input: Union[str, List[str]]) -> List[str]:
  """expand range to member list; input: one item, range, list of either"""
  if not range_input:
    return []

  # normalize to list
  items = [range_input] if isinstance(range_input, str) else range_input
  
  if not isinstance(items, list):
    log.warning(f'range must be string or list, got {type(range_input)}')
    return []

  expanded = []
  for item in items:
    if not isinstance(item, str):
      log.warning(f'range must be string, got {type(item)}')
      continue

    try:
      if ':' in item and item.count(':') == 1:
        start, end = item.split(':')
        expanded.extend(AlphaNumHelper.sequence(start, end))
      else:
        expanded.append(item)
    except Exception as e:
      log.warning(f'error expanding member {item}: {e}')
      expanded.append(item)  # fallback to original

  return expanded


class AlphaNumHelper:
  """utilities for base36 alphanumeric operations"""

  BASE36_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

  @classmethod
  def increment(cls, value: Union[str, int, None] = None) -> str:
    """increment base36 string by 1"""
    normalized = cls._to_string(value)
    if not normalized:
      return '0'

    chars = list(normalized)
    carry = True

    for i in range(len(chars) - 1, -1, -1):
      if not carry:
        break

      if chars[i] == '9':
        chars[i] = 'A'
        carry = False
      elif chars[i] == 'Z':
        chars[i] = '0'
      else:
        chars[i] = chr(ord(chars[i]) + 1)
        carry = False

    if carry:
      chars.insert(0, '1')

    return ''.join(chars)

  @classmethod
  def sequence(cls, 
               start: Union[str, int, None] = None,
               end: Union[str, int, None] = None
               ) -> Generator[str, None, None]:
    """generate base36 sequence from start to end (inclusive)"""
    start_str = cls._to_string(start)
    end_str = cls._to_string(end)

    if not start_str or not end_str:
      log.warning('both start and end required for sequence')
      return

    start_int = cls.to_int(start_str)
    end_int = cls.to_int(end_str)

    if start_int > end_int:
      return

    for i in range(start_int, end_int + 1):
      yield cls.from_int(i).zfill(3)

  @classmethod
  def to_int(cls, base36: str) -> int:
    """convert base36 string to integer"""
    return int(base36, 36)

  @classmethod
  def from_int(cls, num: int) -> str:
    """convert integer to base36 string"""
    if num == 0:
      return '0'

    result = ''
    while num > 0:
      result = cls.BASE36_CHARS[num % 36] + result
      num //= 36

    return result

  @classmethod
  def _to_string(cls, 
                 value: Union[str, int, None]) -> Optional[str]:
    """normalize input to string or return None if invalid"""
    if not value and value != 0:
      return None

    if isinstance(value, int):
      return str(value)
    elif isinstance(value, str):
      return value
    else:
      log.warning(f'value must be string or integer, got {type(value)}')
      return None


class HTMLRequestHelper:
  DEFAULT_TIMEOUT: int = 5
  DEFAULT_SLEEP: int = 3
  DEFAULT_MAX_RETRIES: int = 3

  USER_AGENTS: List[str] = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) '
    'Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) '
    'Gecko/20100101 Firefox/132.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    ]

  @classmethod
  def get_headers(cls, idx: int = -1) -> Dict[str, str]:
    """get request headers with user agent rotation"""
    return {"User-Agent": random.choice(cls.USER_AGENTS)}
  
  @classmethod
  def get_headers_by_index(cls, idx: int) -> Dict[str, str]:
    """get request headers with user agent rotation"""
    return {"User-Agent": cls.USER_AGENTS[idx % len(cls.USER_AGENTS)]}


class URLHelper:
  DOMAIN_PATTERN = (r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
                    r'(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'
                    r'\.[a-zA-Z]{2,}$')

  @classmethod
  def extract_domain(cls, url: Optional[str] = None) -> Optional[str]:
    if url:
      extracted = tldextract.extract(url)
      domain = f'{extracted.domain}.{extracted.suffix}'
      domain = domain.lower().strip()
      if cls.is_valid_domain(domain):
        return domain
    return None


  @classmethod
  def is_valid_domain(cls, domain: str) -> bool:
    if not domain:
      return False

    return bool(re.match(cls._DOMAIN_PATTERN, domain))

  @classmethod
  def is_valid_url(cls, url: str) -> bool:
    """validate url format"""
    try:
      result = urlparse(url)
      return all([result.scheme, result.netloc])
    except Exception as e:
      log.warning(f'invalid url format: {url}, error: {e}')
      return False