import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from utils.access import DriveManager


log = logging.getLogger(__name__)


def load_json(drive_manager: DriveManager, file_path: str
              ) -> Dict[str, Any]:
  file_path = drive_manager.config.resolve_path(file_path)
  content = drive_manager.read_or_none(file_path)
  if not content:
    return {}
  
  try:
    return json.loads(content)
  except json.JSONDecodeError as e:
    log.warning(f'{e}')
    return {}


def write_json_list(drive_manager: DriveManager, matches_name: str,
                    matches: List[Dict[str, Any]]):
  """mostly for beta"""
  dir_views = drive_manager.config.DIR_DATA + 'beta/'
  dir_views = drive_manager.config.resolve_path(dir_views)
  drive_manager.write_or_false(dir_views + matches_name + '.json',
                               json.dumps(matches))
  piped = '\n'.join('|'.join(str(v).replace('\n', ' ') 
                             for v in item.values()) 
                    for item in matches)
  drive_manager.write_or_false(dir_views + matches_name + '.txt', piped)


class EntityManager:
  """manages entity-specific items stored as JSON"""
  _DEFAULT_KEY: str = 'default'
  _MERGED_KEY: str = 'merged'
  _DEFAULT_FILENAME: str = 'default.json'
  _META_KEY: str = '_meta'

  def __init__(self,
               drive_manager: Optional[DriveManager] = None,
               default_path: Optional[Union[str, Path]] = None,
               custom: Optional[Union[str, Dict[str, Any], Path]] = None):
    """
    args:
      default_path: path to default entity file (package resource)
      custom_path: path to custom entities file (user/system location)  
      custom_data: direct dict data (for backward compatibility)
    """
    self._drive_manager = drive_manager
    self._default_path = default_path or str(
        Path(__file__).parent / self._DEFAULT_FILENAME)
    self.entities: Dict[str, Any] = {}

    self._load_entities(custom)

  def get_entity(self, key: str) -> Dict[str, Any]:
    """get entity for key, merging with default if needed"""
    if key not in self.entities:
      return self.entities[self._DEFAULT_KEY]

    if self._MERGED_KEY not in self.entities[key]:
      self._merge_entity(key)

    return self.entities[key]

  def _load_entities(self,
                     source: Optional[Union[str, Path, Dict[str, Any]]]
                     ) -> None:
    """load entities from file or dict"""
    if isinstance(source, dict):
      self.entities = source
    elif source is None:
      self.entities = self._load_json(self._default_path)
    elif isinstance(source, str) or isinstance(source, Path):
      default = self._load_json(self._default_path)
      custom = self._load_json(source)
      self.entities = self._merge_dicts(default, custom)
    else:
      raise TypeError(f"source must be str, dict, or None, got "
                      f"{type(source)}")

  def _load_json(self, path: Union[str, Path]) -> Dict[str, Any]:
    """load json file with error handling"""
    config = load_json(self._drive_manager, path)
    return config or {self._DEFAULT_KEY: {}}

  def _merge_dicts(self, default: Dict[str, Any],
                   custom: Dict[str, Any]) -> Dict[str, Any]:
    """merge default and custom json, preserving both _meta sections"""
    merged = {**default, **custom}

    # special handling for _meta to combine both sections
    if self._META_KEY in default and self._META_KEY in custom:
      merged[self._META_KEY] = {**default[self._META_KEY],
                                **custom[self._META_KEY]}

    return merged

  def _merge_entity(self, key: str) -> None:
    """merge default with custom and mark as merged"""
    default = self.entities[self._DEFAULT_KEY]
    entity = self.entities[key]
    self.entities[key] = self._prepend_entity(default, entity)
    self.entities[key][self._MERGED_KEY] = True

  def _prepend_entity(self, base: Dict[str, Any], 
                      overlay: Dict[str, Any]) -> Dict[str, Any]:
    """merge custom overlay onto default base (overlay takes precedence)"""
    result = base.copy()

    for k, v in overlay.items():
      if k not in result:
        result[k] = v
      elif isinstance(v, dict) and isinstance(result[k], dict):
        result[k] = self._prepend_entity(result[k], v)
      elif isinstance(v, list) and isinstance(result[k], list):
        result[k] = v + result[k]
      else:
        result[k] = v

    return result