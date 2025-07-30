import io
import grp
import logging
import os
import pwd
import stat
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import gspread
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

log = logging.getLogger(__name__)


class PathConfig(ABC):
  """base configuration for path handling"""

  @property
  @abstractmethod
  def is_cloud(self) -> bool:
    """whether this configuration represents cloud storage"""
    pass

  @property
  @abstractmethod
  def default_drive(self) -> str:
    """default drive/root path for this configuration"""
    pass

  def resolve_path(self, path: Union[str, Path]) -> str:
    """generic path resolution - expand user paths and join with drive root"""
    path = str(path)
    expanded_path = os.path.expanduser(path)
    if expanded_path.find(self.default_drive) < 0:
      return str(Path(self.default_drive) / expanded_path)
    else:
      return str(expanded_path)


class GoogleDriveManager:
  def __init__(self,
               credentials_path='~/.config/gspread/authorized_user.json'):
    """initialize google drive manager with credentials"""
    credentials_path = os.path.expanduser(credentials_path)
    creds = Credentials.from_authorized_user_file(credentials_path)
    self.drive_service = build('drive', 'v3', credentials=creds)

  def file_exists(self, file_path: str) -> bool:
    """check if a file exists at the given path in google drive"""
    try:
      parts = [p for p in file_path.split('/') if p]
      filename = parts[-1]
      folder_path = parts[:-1]

      # get folder ID (will raise FileNotFoundError if folder doesn't exist)
      folder_id = self._get_folder_id(folder_path)

      # search for file in the folder
      query = (f"name='{filename}' and '{folder_id}' in parents "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      files = results.get('files', [])

      return len(files) > 0

    except FileNotFoundError:
      # folder doesn't exist, so file doesn't exist
      return False
    except Exception as e:
      raise Exception(f"error checking if file exists '{file_path}': "
                      f"{str(e)}")

  def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
    """get detailed info about a file if it exists"""
    try:
      parts = [p for p in file_path.split('/') if p]
      filename = parts[-1]
      folder_path = parts[:-1]

      # get folder ID
      folder_id = self._get_folder_id(folder_path)

      # search for file with more details
      query = (f"name='{filename}' and '{folder_id}' in parents "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query,
        fields='files(id,name,size,createdTime,modifiedTime,mimeType)'
      ).execute()
      files = results.get('files', [])

      if not files:
        return None

      return files[0]  # return first match with full details

    except FileNotFoundError:
      return None
    except Exception as e:
      raise Exception(f"error getting file info '{file_path}': {str(e)}")

  def read_file(self, file_path: str) -> Optional[str]:
    """read file content from google drive by path"""
    try:
      parts = [p for p in file_path.split('/') if p]
      filename = parts[-1]
      folder_path = parts[:-1]

      # get folder ID
      folder_id = self._get_folder_id(folder_path)

      # find file in folder
      query = (f"name='{filename}' and '{folder_id}' in parents "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      files = results.get('files', [])

      if not files:
        raise FileNotFoundError(
          f"file '{filename}' not found in path '{file_path}'")

      # read file content
      content = self.drive_service.files().get_media(
        fileId=files[0]['id']).execute()
      return content.decode('utf-8')

    except UnicodeDecodeError:
      # if it's not a text file, return bytes
      return content
    except Exception as e:
      raise Exception(f"error reading file '{file_path}': {str(e)}")

  def write_file(self, file_path: str, content: str):
    """write content to file in google drive"""
    try:
      parts = [p for p in file_path.split('/') if p]
      filename = parts[-1]
      folder_path = parts[:-1]

      # get or create folder structure
      folder_id = self._get_or_create_folder_path(folder_path)

      # check if file already exists
      query = (f"name='{filename}' and '{folder_id}' in parents "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      existing_files = results.get('files', [])

      # prepare content for upload
      if isinstance(content, str):
        media = MediaIoBaseUpload(
          io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
      else:
        media = MediaIoBaseUpload(
          io.BytesIO(content), mimetype='application/octet-stream')

      if existing_files:
        # update existing file
        file_id = existing_files[0]['id']
        self.drive_service.files().update(
          fileId=file_id, media_body=media).execute()
        log.info(f"updated existing file: {file_path}")
      else:
        # create new file
        file_metadata = {
          'name': filename,
          'parents': [folder_id]
        }
        self.drive_service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id'
        ).execute()
        log.info(f"created new file: {file_path}")

    except Exception as e:
      raise Exception(f"error writing file '{file_path}': {str(e)}")

  def upload_file_from_url(self, url: str, file_path: str,
                           filename: str = None) -> None:
    """download file from URL and upload to google drive"""
    try:
      # use filename from URL if not provided
      if not filename:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
          filename = 'downloaded_file'

      parts = [p for p in file_path.split('/') if p]
      folder_path = parts

      # get or create folder structure
      folder_id = self._get_or_create_folder_path(folder_path)

      # download file to temporary location
      log.info(f"downloading file from {url}")
      response = requests.get(url, stream=True)
      response.raise_for_status()

      # get MIME type from response headers
      content_type = response.headers.get('content-type', 
                                          'application/octet-stream')

      # create temporary file
      with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
          temp_file.write(chunk)
        temp_path = temp_file.name

      try:
        # check if file already exists
        query = (f"name='{filename}' and '{folder_id}' in parents "
                 f"and trashed=false")
        results = self.drive_service.files().list(
          q=query, fields='files(id)').execute()
        existing_files = results.get('files', [])

        # upload file
        media = MediaFileUpload(temp_path, mimetype=content_type)

        if existing_files:
          # update existing file
          file_id = existing_files[0]['id']
          self.drive_service.files().update(
            fileId=file_id, media_body=media).execute()
          log.info(f"updated existing file: {file_path}/{filename}")
        else:
          # create new file
          file_metadata = {
            'name': filename,
            'parents': [folder_id]
          }
          self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
          ).execute()
          log.info(f"uploaded new file: {file_path}/{filename}")

      finally:
        # clean up temporary file
        os.unlink(temp_path)

    except requests.RequestException as e:
      raise Exception(f"error downloading from URL '{url}': {str(e)}")
    except Exception as e:
      raise Exception(f"error uploading file from URL: {str(e)}")

  def upload_local_file(self, local_path: str, drive_path: str) -> None:
    """upload local file to google drive"""
    try:
      if not os.path.exists(local_path):
        raise FileNotFoundError(f"local file not found: {local_path}")

      parts = [p for p in drive_path.split('/') if p]
      filename = parts[-1]
      folder_path = parts[:-1]

      # get or create folder structure
      folder_id = self._get_or_create_folder_path(folder_path)

      # determine MIME type
      if local_path.endswith('.pdf'):
        mimetype = 'application/pdf'
      elif local_path.endswith(('.xlsx', '.xls')):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      elif local_path.endswith(('.jpg', '.jpeg')):
        mimetype = 'image/jpeg'
      elif local_path.endswith('.png'):
        mimetype = 'image/png'
      else:
        mimetype = 'application/octet-stream'

      # check if file already exists
      query = (f"name='{filename}' and '{folder_id}' in parents "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      existing_files = results.get('files', [])

      # upload file
      media = MediaFileUpload(local_path, mimetype=mimetype)

      if existing_files:
        # update existing file
        file_id = existing_files[0]['id']
        self.drive_service.files().update(
          fileId=file_id, media_body=media).execute()
        log.info(f"updated existing file: {drive_path}")
      else:
        # create new file
        file_metadata = {
          'name': filename,
          'parents': [folder_id]
        }
        self.drive_service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id'
        ).execute()
        log.info(f"uploaded new file: {drive_path}")

    except Exception as e:
      raise Exception(f"error uploading local file: {str(e)}")

  def _get_folder_id(self, folder_path: str) -> Optional[str]:
    """get folder ID by navigating path (read-only)"""
    if not folder_path:
      return 'root'

    folder_id = 'root'
    for folder_name in folder_path:
      query = (f"name='{folder_name}' and '{folder_id}' in parents "
               f"and mimeType='application/vnd.google-apps.folder' "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      folders = results.get('files', [])

      if not folders:
        raise FileNotFoundError(f"folder '{folder_name}' not found")

      folder_id = folders[0]['id']

    return folder_id

  def _get_or_create_folder_path(self, folder_path: str) -> Optional[str]:
    """get folder ID, creating folders if they don't exist"""
    if not folder_path:
      return 'root'

    folder_id = 'root'
    for folder_name in folder_path:
      query = (f"name='{folder_name}' and '{folder_id}' in parents "
               f"and mimeType='application/vnd.google-apps.folder' "
               f"and trashed=false")
      results = self.drive_service.files().list(
        q=query, fields='files(id)').execute()
      folders = results.get('files', [])

      if folders:
        folder_id = folders[0]['id']
      else:
        # create the folder
        folder_metadata = {
          'name': folder_name,
          'parents': [folder_id],
          'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive_service.files().create(
          body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        log.info(f"created folder: {folder_name}")

    return folder_id


class SheetsClientManager:
  _client: gspread.Client = None

  @classmethod 
  def get_client(cls) -> gspread.Client:
    if cls._client is None:
      # check if service account credentials exist
      service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
      if service_account_path and os.path.exists(service_account_path):
        cls._client = gspread.service_account()
      else:
        cls._client = gspread.oauth()
    return cls._client

  @classmethod
  def open_sheet(cls, sheet_name_or_id: str) -> Optional[gspread.Spreadsheet]:
    """open with automatic session warming on failure"""
    client = cls.get_client()

    try:
      return client.open(sheet_name_or_id)
    except Exception as e:
      print(f"client.open({sheet_name_or_id}): {e}")

    try:
      spreadsheets = client.openall(sheet_name_or_id)
      for spreadsheet in spreadsheets:
        if spreadsheet.title == sheet_name_or_id:
          return spreadsheet
    except Exception as e:
      print(f"client.openall({sheet_name_or_id}): {e}")

    return None

  @classmethod
  def open_worksheet(cls, sheet_name_or_id: str,
                     worksheet_name: str) -> Optional[gspread.Worksheet]:
    spreadsheet = cls.open_sheet(sheet_name_or_id)
    if not spreadsheet:
      return None

    return spreadsheet.worksheet(worksheet_name)


class DriveManager:
  """manages file operations with path configuration"""
  def __init__(self, config: Optional[PathConfig] = None):
    self.config = config
    if self.config.is_cloud:
      self.cloud = self.config.get_cloud_manager()
    else:
      self.cloud = None

  def read(self, file_path: Union[str, Path]) -> str:
    file_path = str(file_path)
    if self.cloud:
      return self.cloud.read_file(file_path)  
    else:
      full_path = self.config.resolve_path(file_path)
      return Path(full_path).read_text()

  def read_or_none(self, file_path: Union[str, Path]) -> str | None:
    try:
      return self.read(file_path)
    except (FileNotFoundError, PermissionError, IOError, OSError) as e:
      log.error(e)
      return None

  def write(self, file_path: Union[str, Path], content: str) -> None:
    file_path = str(file_path)
    if self.cloud:
      self.cloud.write_file(file_path, content)
    else:
      full_path = self.config.resolve_path(file_path)
      Path(full_path).write_text(content)

  def write_or_false(self, file_path: Union[str, Path], content: str) -> bool:
    try:
      self.write(file_path, content)
      return True
    except (PermissionError, IOError, OSError) as e:
      log.error(e)
      return False

  def file_exists(self, file_path: str):
    """check if a file exists at the given path"""
    file_path = str(file_path)
    if self.cloud:
      return self.cloud.file_exists(file_path)
    else:
      path = self.config.resolve_path(file_path)
      return os.path.isfile(path)

  def file_exists_or_false(self, file_path: str):
    try:
      return self.file_exists(file_path)
    except Exception as e:
      log.error(e)
      return False

  def get_file_info(self, file_path: str) -> str:
    """get detailed info about a file if it exists"""
    file_path = str(file_path)
    if self.cloud:
      return self.cloud.get_file_info(file_path)
    else:
      path = self.config.resolve_path(file_path)
      return self._get_file_info_local(path)

  def get_file_info_or_none(self, file_path: str) -> str:
    try:
      return self.get_file_info(file_path)
    except Exception as e:
      log.error(e)
      return None

  def _get_file_info_local(self, file_path: str) -> str:
    path = os.path.expanduser(file_path)

    if not os.path.exists(path):
      return None

    stat_info = os.stat(path)

    # get owner and group names
    try:
      owner = pwd.getpwuid(stat_info.st_uid).pw_name
    except KeyError:
      owner = str(stat_info.st_uid)

    try:
      group = grp.getgrgid(stat_info.st_gid).gr_name
    except KeyError:
      group = str(stat_info.st_gid)

    # format permissions
    permissions = stat.filemode(stat_info.st_mode)

    return {
      'path': path,
      'name': os.path.basename(path),
      'size': stat_info.st_size,
      'is_file': os.path.isfile(path),
      'is_directory': os.path.isdir(path),
      'permissions': permissions,
      'owner': owner,
      'group': group,
      'created_time': datetime.fromtimestamp(stat_info.st_ctime),
      'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
      'accessed_time': datetime.fromtimestamp(stat_info.st_atime)
    }