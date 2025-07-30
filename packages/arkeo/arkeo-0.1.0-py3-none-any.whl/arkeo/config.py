from pathlib import Path
from utils.access import PathConfig


class ArticlePathConfig(PathConfig):
  """base configuration for article path handling"""

  DIR_SYSTEM: str = None
  DIR_CONFIG: str = None
  DIR_DATA: str = None
  DIR_CORPUS: str = None
  DIR_INDEXES: str = None
  DIR_RAW: str = None
  DIR_VIEWS: str = None

  DEFAULT_PARSE = Path(__file__).parent / 'parse_default.json'