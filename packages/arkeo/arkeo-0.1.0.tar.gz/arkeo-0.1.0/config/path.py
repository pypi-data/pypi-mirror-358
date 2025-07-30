from pathlib import Path

from utils.access import GoogleDriveManager

from arkeo.config import ArticlePathConfig


class CloudPathConfig(ArticlePathConfig):
  """configuration for cloud filesystem paths"""

  DIR_SYSTEM = 'arkeo/system/'
  DIR_CONFIG = 'arkeo/system/config/'
  DIR_DATA = 'arkeo/'
  DIR_CORPUS = 'arkeo/corpus/'
  DIR_INDEXES = 'arkeo/indexes/'
  DIR_RAW = 'arkeo/raw/'
  DIR_VIEWS = 'arkeo/views/'

  @property
  def is_cloud(self) -> bool:
    return True

  @property
  def default_drive(self) -> str:
    return ''

  def get_cloud_manager(self) -> None:
    return GoogleDriveManager()


class LocalPathConfig(ArticlePathConfig):
  """configuration for local filesystem paths"""

  DIR_SYSTEM = 'Documents/arkeo/'
  DIR_CONFIG = 'Documents/arkeo/config/'
  DIR_DATA = 'Downloads/arkeo/'
  DIR_CORPUS = 'Downloads/arkeo/corpus/'
  DIR_INDEXES = 'Downloads/arkeo/indexes/'
  DIR_RAW = 'Downloads/arkeo/raw/'
  DIR_VIEWS = 'Downloads/arkeo/views/'

  @property
  def is_cloud(self) -> bool:
    return False

  @property
  def default_drive(self) -> str:
    return str(Path.home())