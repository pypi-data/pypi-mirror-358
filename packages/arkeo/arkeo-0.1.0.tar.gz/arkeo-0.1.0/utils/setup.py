import logging
import os
from typing import Optional

import nltk


log = logging.getLogger(__name__)


def download_nltk_data() -> None:
  """download required NLTK data if not already present"""
  required_data = [
    ('tokenizers/punkt_tab', 'punkt_tab'),
    ('corpora/stopwords', 'stopwords')
  ]

  missing_data = []
  for data_path, download_name in required_data:
    try:
      nltk.data.find(data_path)
    except LookupError:
      missing_data.append(download_name)

  if not missing_data:
    log.info("NLTK data already available")
    return

  log.info(f"downloading NLTK data: {', '.join(missing_data)}")
  for download_name in missing_data:
    nltk.download(download_name, quiet=True)
  log.info("NLTK data download complete")


def setup_logging(log_to_screen: bool = True, 
                  level: int = logging.WARNING,
                  filename: str = 'default.log', 
                  path: Optional[str] = None) -> logging.Logger:
  """setup logging with screen or file output"""

  # cleanup existing handlers
  for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

  config = {
    'level': level,
    'format': '%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s',
    'force': True
  }

  if not log_to_screen:
    if path and os.path.exists(path):
      filename = os.path.join(path, filename)
    config.update({'filename': filename, 'filemode': 'a'})

  logging.basicConfig(**config)
  return logging.getLogger(__name__)


def setup_all(log_to_screen: bool = True, 
              level: int = logging.WARNING,
              filename: str = 'default.log', 
              path: Optional[str] = None) -> logging.Logger:
  """initialize all setup components"""
  logger = setup_logging(log_to_screen, level, filename, path)
  download_nltk_data()
  return logger