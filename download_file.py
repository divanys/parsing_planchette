import requests


def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/uc?id=" + file_id
    response = requests.get(URL, stream=True)

    if response.status_code == 200:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Файл успешно скачан и сохранен по пути: {destination}")
    else:
        print("Не удалось скачать файл. Проверьте вашу ссылку.")