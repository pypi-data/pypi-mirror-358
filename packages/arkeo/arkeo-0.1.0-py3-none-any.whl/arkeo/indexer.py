import fcntl
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from typing import Any, Dict, List, Optional, Union

from arkeo.utils import (
  convert_markdown_to_text, 
  format_nav_path, 
  is_nav_key_format
)
from geonames import GeonamesManager
from utils.access import DriveManager
from utils.json import load_json, write_json_list
from utils.search import ContextManager, KeywordsManager
from utils.text import AlphaNumHelper, expand_to_list


log = logging.getLogger(__name__)


class ArticleIndexer:

  FILE_PK: str = 'pk.json'
  FILE_SEQ: str = 'pk_seq.json'

  def __init__(self, driver_manager: DriveManager):
    self.dm = driver_manager
    self._cm = ContextManager()
    self._km = KeywordsManager(GeonamesManager())
    
    dir_cfg = self.dm.config.DIR_CONFIG
    self._cx_labor = load_json(self.dm, dir_cfg + 'context_labor.json')
    self._cx_money = load_json(self.dm, dir_cfg + 'context_money.json')

  @property
  def pk_path(self) -> Path:
    return Path(self.dm.config.DIR_INDEXES) / self.FILE_PK
  
  @property
  def seq_path(self) -> Path:
    return Path(self.dm.config.DIR_INDEXES) / self.FILE_SEQ
  
  def build(self, source: Optional[str] = None) -> bool:
    """one nav_key (YYYY-mm-pk) or multiple pks or none"""
    if source and isinstance(source, str) and is_nav_key_format(source):
      data = self.index_item(source, True)
      file_name = f'{source}.json'
    else:
      if source:
        source = source.split(',')
      data = self.index_items(source)
      file_name = 'view.json'

    if not data:
      log.warning(f'{file_name}, no data to write')
      return False
    else:
      file_path = self.dm.config.DIR_VIEWS + file_name
      if not self.dm.write_or_false(file_path, json.dumps(data)):
        log.warning(f'{file_path}, write failure')
        return False
      return True

  def index_items(self, keys: Union[str, List[str], Dict[str, Dict[str, str]]] = None) -> List[Dict]:
    results = []

    if not (keys and isinstance(keys, dict)):
      pks = load_json(self.dm, self.pk_path)
      if keys:
        # build dict from selected keys only
        keys = {k: pks[k] for k in expand_to_list(keys) if k in pks}
      else:
        keys = pks

    for data in tqdm(keys.values(), desc="indexing articles"):
      item = self.index_item(data["nav_key"])
      if item:
        item['url'] = data['url']
        results.append(item)
    
    return results

  def index_item(self, nav_key: str, beta: bool = False) -> Dict[str, Any]:
    file_path = self.dm.config.DIR_CORPUS + format_nav_path(nav_key)

    for ext in ['.md', '.txt']:
      if self.dm.file_exists(file_path + ext):
        body_text = self.dm.read(file_path + ext)
        if ext == '.md':
          body_text = convert_markdown_to_text(body_text)
        break
    else:
      return {}

    labor_matches = self._cm.extract_content(body_text, self._cx_labor)
    money_matches = self._cm.extract_content(body_text, self._cx_money)

    if not (labor_matches or money_matches):
      return {}

    # TODO: remove or retool beta
    if beta:
      write_json_list(self.dm, f'{nav_key}-labor', labor_matches)
      write_json_list(self.dm, f'{nav_key}-money', money_matches)

    return {
      'nav_key': nav_key,
      'url': file_path,
      'data': (self._wrap_data('labor', labor_matches) |
               self._wrap_data('money', money_matches) | 
               self._wrap_data('geoloc', self._km.find_all(body_text)))}

  def get_next_pk(self) -> str:
    if self.dm.cloud:
      data = load_json(self.dm, self.seq_path)
      new_key = self._update_sequence_data(data)
      self.dm.write(self.seq_path, json.dumps(data, indent=2))
      return new_key
    else:
      seq_path = self.dm.config.resolve_path(self.seq_path)
      with open(seq_path, 'r+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
          content = f.read()
          data = json.loads(content) if content else {}
          new_key = self._update_sequence_data(data)
        except (json.JSONDecodeError, ValueError):
          data = {}
        
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

        return new_key

  def update_pk(self, key: str, value: Dict[str, str]) -> None:
    """insert new key before closing brace"""
    
    if self.dm.cloud:
      data = load_json(self.dm, self.pk_path)
      data[key] = value
      self.dm.write(self.pk_path, json.dumps(data, indent=2))
    else:
      pk_path = self.dm.config.resolve_path(self.pk_path)
      with open(pk_path, 'r+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        f.seek(0, os.SEEK_END)
        # TODO: verify last three chars / between server defaults
        f.seek(f.tell()-3)
        f.truncate()
        
        # append new key
        f.write(f',\n"{key}": {json.dumps(value)}')
        f.write('\n}')  # reclose structure

        f.flush()

  def _update_sequence_data(self, data: Dict[str, Any]) -> str:
    max_key = data.get('max_key', '000')
    new_key = AlphaNumHelper.increment(max_key)
    data['max_key'] = new_key
    data['last_updated'] = datetime.now().isoformat()
    return new_key

  def _wrap_data(self, key: str,
                 data: Dict[str, Any]) -> Dict[str, Any]:
    wrapped = {}
    wrapped[key] = data
    return wrapped