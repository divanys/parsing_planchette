from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import Links

path_to_credentials_json = 'client_secrets.json'

folder_id = Links.folder_id

DOWNLOAD_DIR = Links.DOWNLOAD_DIR
gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

for file in file_list:
    file.GetContentFile(DOWNLOAD_DIR + file['title'])
    print(f"Downloaded: {DOWNLOAD_DIR}{file['title']}")
