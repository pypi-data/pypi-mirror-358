import logging
import re
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional

from flashtext import KeywordProcessor

from geonames import GeonamesManager


log = logging.getLogger(__name__)


class ContextAction(Enum):
  """context action"""
  INDICATE = 'indicate'
  SEARCH = 'search'
  REMOVE = 'remove'


class ContextManager:
  """manages text context extraction based on configurable patterns"""

  # regex constants
  WORD_BOUNDARY: str = r'\b'
  RE_MMDDYYYY: str = r'\d{1,2}/\d{1,2}/\d{2,4}'
  RE_MODDYYYY: str = (r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|'
                      r'apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|'
                      r'sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|'
                      r'dec(?:ember)?)\s+(\d{1,2},\s+)?\d{4}')

  CONTEXT_BUFFER = 150
  COMPARE_BUFFER = 50

  CONFIG_KEY: str = '_meta.name'
  PATTERN_KEY_DATE: str = 'date'
  PATTERN_KEY_ADJACENT: str = 'adjacent'

  def __init__(self) -> None:
    self._action_exprs: Dict[str, Any] = {}
    self._setup_default_expressions()

  def _setup_default_expressions(self) -> None:
    """initialize default date patterns"""
    patterns = {'mdY': self.RE_MMDDYYYY, 'MdY': self.RE_MODDYYYY}
    exprs = {name: re.compile(pattern, re.IGNORECASE) 
             for name, pattern in patterns.items()}
    self._action_exprs['default'] = {self.PATTERN_KEY_DATE: exprs}

  def extract_content(self, text: str,
                      config: Dict[str, Any]) -> Dict[str, Any]:
    """extract context matches based on configuration"""

    if not text or not config:
      return {}

    actions = self._get_actions(config)
    if not actions:
      return {}

    # include if indicated
    if not self._has_indication(text, actions):
      return {}

    # extract matches
    search_patterns = actions.get(ContextAction.SEARCH.value, {})
    if not search_patterns:
      return {}

    remove_patterns = actions.get(ContextAction.REMOVE.value, {})

    return self._find_matches(text, search_patterns, remove_patterns)

  def _has_indication(self, text: str, actions: Dict[str, Any]) -> bool:
    """find and filter pattern matches"""
    indicate_exprs = actions.get(ContextAction.INDICATE.value, {})
    return any(expr.search(text) for expr in indicate_exprs.values())

  def _find_matches(self, text: str, search_patterns: Dict[str, re.Pattern],
                    remove_patterns: Dict[str, Any]) -> List[Dict]:
    """find and filter pattern matches"""
    matches = []

    for search_name, search_expr in search_patterns.items():
      for match in search_expr.finditer(text):
        start, group = match.start(), match.group()
        compare = self._extract_context_window(text, start, len(group),
                                               self.COMPARE_BUFFER)

        if not self._is_removed(group, compare, remove_patterns):
          context = self._extract_context_window(text, start, len(group),
                                                 self.CONTEXT_BUFFER)
          if self._validated_uniqueness(group, context, compare, matches):
            matches.append({
              'loc': start,
              'match': group,
              'context': context  #, 'pattern': search_name, 'compare': compare
            })

    return matches

  def _extract_context_window(self, text: str, start_pos: int,
                              match_len: int, buffer_size: int) -> str:
    """extract content window around match"""
    remaining_buffer = buffer_size - match_len
    context_start = max(0, start_pos - remaining_buffer//2)
    return text[context_start:context_start + buffer_size]

  def _is_removed(self, match: str, context: str,
                  remove_patterns: Dict[str, Any]) -> bool:
    """check if match should be removed based on context"""
    for pattern_name, pattern in remove_patterns.items():
      if self._matches_remove_pattern(match, context, pattern_name, pattern):
        return True
    return False

  def _matches_remove_pattern(self, match: str, context: str, 
                              pattern_name: str, pattern: Any) -> bool:
    """check individual remove pattern"""
    if pattern_name == self.PATTERN_KEY_ADJACENT and isinstance(pattern, str):
      word = self._build_word(match)
      return (re.search(pattern + r'\s' + word, context, re.IGNORECASE) or 
              re.search(word + r'\s' + pattern, context, re.IGNORECASE))

    if isinstance(pattern, dict):
      return any(expr.search(context) for expr in pattern.values())

    if hasattr(pattern, 'search'):
      return pattern.search(context) is not None

    return False

  def _build_word(self, pattern: str) -> str:
    return f'{self.WORD_BOUNDARY}{pattern}{self.WORD_BOUNDARY}'

  def _validated_uniqueness(self, group: str, context: str, compare: str,
                           matches: List[Dict[str, Any]]) -> bool:
    group_len = len(group)
    downsize = (self.CONTEXT_BUFFER - self.COMPARE_BUFFER) // 2
    
    for i in range(len(matches) - 1, -1, -1):
      match = matches[i]
      match_len = len(match.get('match', ''))
      match_context = match.get('context', '')
      
      if group_len > match_len:
        if compare in match_context:
          matches.pop(i)
      else:
        match_compare = match_context[downsize:downsize+self.COMPARE_BUFFER]
        if match_compare in context:
          return False
    
    return True

  def _get_actions(self, config: Dict[str, Any]) -> Dict[str, Any]:
    config_key = self._extract_config_key(config)
    if not config_key:
      return {}

    if config_key in self._action_exprs:
      return self._action_exprs[config_key]

    actions = self._build_actions(config)
    if actions:
      self._action_exprs[config_key] = actions

    return actions

  def _build_actions(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """build action patterns from config"""
    actions = {}

    for action in [ca.value for ca in ContextAction]:
      if action not in config:
        continue

      actions[action] = {}
      for pattern_name, pattern in config[action].items():
        processed_pattern = self._process_pattern(
          action, pattern_name, pattern, config)
        actions[action][pattern_name] = processed_pattern
    
    return actions

  def _process_pattern(self, action: str, pattern_name: str, pattern: str,
                      config: Dict[str, Any]) -> re.Pattern:
    """process individual pattern based on action type"""
    if action == ContextAction.SEARCH.value:
      pattern = self._build_word(pattern)
    
    if action == ContextAction.REMOVE.value:
      if pattern_name == self.PATTERN_KEY_DATE and not pattern:
        return self._get_default_date_patterns()
      if pattern_name == self.PATTERN_KEY_ADJACENT:
        return pattern
    
    return re.compile(pattern, re.IGNORECASE)

  def _get_default_date_patterns(self) -> Dict[str, re.Pattern]:
    """get default date patterns"""
    default_actions = self._action_exprs.get('default', {})
    return default_actions.get(self.PATTERN_KEY_DATE, {})

  def _extract_config_key(self, config: Dict[str, Any]) -> str:
    try:
      keys = self.CONFIG_KEY.split('.')
      return config[keys[0]][keys[1]]
    except Exception as e:
      log.warning(f'malformed input configuration: {e}')
      return ''


class KeywordsManager:

  # methods, initilization
  def __init__(self, geonames_manager: Optional[GeonamesManager] = None):
    self.geonames_manager = geonames_manager

    # [ST,name,alts]
    self._states = self.geonames_manager.list_geo(self.geonames_manager.STATES)
    self._states_by_name = {state[1]: state[0] for state in self._states}
    self._states_by_alt = {state[2]: state[0] for state in self._states}
    self._kwp_states = self._get_keyword_processor_for_states()

    # [name,ST,flag]
    self._cities = self._make_locations_unique(self.geonames_manager.CITIES)
    self._kwp_cities = self._set_keyword_processor_for_unique_locations(
                         self.geonames_manager.CITIES)
    # [name,ST,flag]
    self._munis = self._make_locations_unique(self.geonames_manager.MUNIS)
    self._kwp_munis = self._set_keyword_processor_for_unique_locations(
                        self.geonames_manager.MUNIS)

  def _get_keyword_processor_for_states(self, states: Any = None
                                        ) -> Optional[KeywordProcessor]:
    if states is None:
      states = self._states
    elif isinstance(states, list) and states:
      if isinstance(states[0], str):
        states = self._get_subset_states(states)
      elif not isinstance(states[0], list):
        return None  # malformed
    else:
      return None  # invalid type

    if not states:
      return None

    kwp = KeywordProcessor()
    for state in states:
      kwp.add_keyword(state[1])  # add name
      if len(state) > 2 and state[2]:
        kwp.add_keyword(state[2])  # add alt-names
    return kwp

  def _set_keyword_processor_for_unique_locations(self, location: str
                                                  ) -> KeywordProcessor:
    locations = (self._munis if location == self.geonames_manager.MUNIS 
                 else self._cities)
    kwp = KeywordProcessor()
    for key, loc in locations.items():
      if loc and not isinstance(loc, list):
        kwp.add_keyword(key)
    return kwp

  # methods, data processing
  def _make_locations_unique(self, location: str) -> Dict[str, Any]:
    # [name,ST,flag]
    locations = self.geonames_manager.list_geo(location)
    unique = {}
    for location in locations:
      if location[0] in unique:
        unique[location[0]].append(location[1])
      elif location[2] == 1:  # flag 1 ↦ keyword search requires name, state
        unique[location[0]] = [location[1]]
      else:
        unique[location[0]] = location[1]
    return unique

  def _get_subset_states(self, selected: List[str]) -> List[List[str]]:
    select_set = set(selected)
    return [row for row in self._states if row[0] in select_set]

  # methods, search/find ops
  def find_states(self, text: str, kwp: KeywordProcessor = None) -> List[str]:
    kwp = kwp or self._kwp_states
    unique_states = []
    for found in kwp.extract_keywords(text):
      if found in self._states_by_name:
        unique_states.append(self._states_by_name[found])
      elif found in self._states_by_alt:
        unique_states.append(self._states_by_alt[found])
    return list(set(unique_states))

  def find_locations(self, location: str, text: str,
                     kwp: KeywordProcessor = None) -> Dict[str, str]:
    if location == self.geonames_manager.MUNIS:
      kwp = kwp or self._kwp_munis
      locations = self._munis
    else:
      kwp = kwp or self._kwp_cities
      locations = self._cities

    unique_locations = {}
    for unique_name in kwp.extract_keywords(text):
      unique_locations[unique_name] = locations[unique_name]
    # non-unique locations that exist in multiple states
    flagged_locations = self._find_locations_flagged(location, text)
    return {**unique_locations,**flagged_locations}

  def _find_locations_flagged(self, location: str,
                              text: str) -> Dict[str, str]:
    locations = (self._munis if location == self.geonames_manager.MUNIS
                 else self._cities)
    found = {}

    # simple filter bc only one flag value
    for location in locations:
      states = locations[location]
      if isinstance(states, list):
        for state in states:
          one_row = self._get_subset_states([state])[0]
          state_names = (one_row[0],one_row[1],one_row[2])
          state_pattern = KeywordsManager.get_compiled_pattern(location,
                                                               state_names)
          if state_pattern.search(text):
            found[location] = state
            break
    return found

  def find_all_city_states(self, text: str) -> Dict[str, str]:
    found_states = self.find_states(text)
    found_locations = {**self.find_locations(self.geonames_manager.CITIES,
                                             text),
                       **self.find_locations(self.geonames_manager.MUNIS,
                                             text)}

    # filter out states that conflict with found locations
    filtered_states = [
      state for state in found_states
      if not any(
        state == self._states_by_name.get(city) or state in city_state
        for city, city_state in found_locations.items()
        )
    ]

    # add remaining states to locations
    found_locations.update({f'[{state}]': state for state in filtered_states})

    return found_locations

  def find_all(self, text: str) -> Dict[str, str]:
    by_state = {}
    by_city = self.find_all_city_states(text)
    for city in by_city:
      state = by_city[city]
      if city.startswith('['):
        city_name = ''
      else:
        city_name = city
      if state in by_state:
        by_state[state].append(city_name)
      else:
        by_state[state] = [city_name]
    return by_state

  # methods, utilities
  @staticmethod
  @lru_cache(maxsize=128)
  def get_compiled_pattern(city_name: str, state: tuple,
                           max_distance: int=100) -> re.Pattern:
    state_pattern = "|".join(filter(None, state))
    return re.compile(
      rf'{re.escape(city_name)}(?=.{{0,{max_distance}}}(?:{state_pattern}))')