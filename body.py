from datetime import datetime
import os
import pickle
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import to_json
from download_file import download_file_from_google_drive

import Links

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
TOKEN_PICKLE_FILE = Links.TOKEN_PICKLE_FILE
OUTPUT_JSON_FILE = Links.OUTPUT_JSON_FILE
DOWNLOAD_DIR = Links.DOWNLOAD_DIR
SECRET = Links.SECRET


def get_drive_service():
    credentials = None

    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES)
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    return build('drive', 'v3', credentials=credentials)


def delete_old_files(directory):
    current_date = datetime.now()

    files = os.listdir(directory)

    for file in files:
        file_path = os.path.join(directory, file)

        file_name, file_extension = os.path.splitext(file)
        try:
            file_date = datetime.strptime(file_name, "%d.%m.%Y")
        except ValueError:
            continue
        days_difference = (current_date - file_date).days
        if days_difference > 2:
            os.remove(file_path)
            print(f"Файл {file} удален.")
        else:
            print(f"Файл {file} не удален.")


def list_files_in_folder(service, folder_id):
    results = service.files().list(
        pageSize=10,
        q=f"'{folder_id}' in parents",
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    all_items = {}
    if not items:
        print('No files found in the specified folder.')
    else:
        for item in items:
            file_name = item["name"]
            file_id = item["id"]
            all_items[file_name] = file_id

    return all_items


def download_files_from_json(json_file_path, download_dir):
    with open(json_file_path, 'r') as json_file:
        files_data = json.load(json_file)

    for file_name, file_url in files_data.items():
        download_file_from_google_drive(file_url, os.path.join(download_dir, file_name))
        print(f'File {file_name} downloaded to {download_dir}')


def download_and_process_updates(updated_files):
    for file_name, file_id in updated_files.items():
        download_path = os.path.join(DOWNLOAD_DIR, file_name)
        download_file_from_google_drive(file_id, download_path)
        print(f'File {file_name} downloaded to {download_path}')

        to_json.parse_and_convert_to_json(download_path)
        print(f'File {file_name} processed and converted to JSON')


if __name__ == '__main__':
    while True:
        delete_old_files(DOWNLOAD_DIR)

        service = get_drive_service()

        folder_id = Links.folder_id

        files_data = list_files_in_folder(service, folder_id)

        with open(OUTPUT_JSON_FILE, 'w') as json_file:
            json.dump(files_data, json_file, indent=2)

        download_files_from_json(OUTPUT_JSON_FILE, DOWNLOAD_DIR)

        print(f'Files downloaded to {DOWNLOAD_DIR}')
        to_json.parse_and_convert_to_json(DOWNLOAD_DIR)
        time.sleep(180)  # Пауза в 10 cek
