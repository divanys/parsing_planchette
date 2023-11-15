# import requests
# from bs4 import BeautifulSoup
#
# url = 'https://drive.google.com/drive/folders/19yyXXullGGMIT3XISiZ33wkDxHJy0zvb/'
#
# r = requests.get(url).text
# soup = BeautifulSoup(r, 'lxml')
# anel = soup.find('div', attrs={'class': "g3Fmkb"})
# anel1 = anel.find("div", attrs={"class": "PolqHc"})
# anel2 = anel1.find("div", attrs={"class": "iZmuQc"})
#
# for i in range(len(anel2)):
#     anel3 = anel2.find_all("div", attrs={"role": "row"})
#     anel4 = anel3[i].find("div", attrs={"class": "KL4NAf"})
#     print(anel3[i])
# file_name = anel4.text
# url_download = url + f"{file_name}"
#
# response = requests.get(url_download)
#
# with open(file_name, 'wb') as file:
#     file.write(response.content)

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import gdown
# import re
#
# url = 'https://drive.google.com/drive/folders/19yyXXullGGMIT3XISiZ33wkDxHJy0zvb/'
#
# # Настройки для браузера
# chrome_options = Options()
# chrome_options.headless = True
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920x1080")
#
# # Используйте ChromeDriverManager для автоматической установки драйвера
# chrome_service = ChromeService(ChromeDriverManager().install())
#
# # Запустите браузер
# driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
#
# try:
#     # Загрузите страницу
#     driver.get(url)
#
#     # Подождите, чтобы браузер успел загрузить контент
#     time.sleep(5)
#
#     # Используйте Selenium для извлечения данных
#     file_containers = driver.find_elements(By.XPATH, '//div[@role="row"]')
#
#     for file_container in file_containers:
#         file_name_element = file_container.find_element(By.XPATH, './/div[@class="KL4NAf"]')
#         file_name = file_name_element.text.strip()
#
#         # Используйте регулярное выражение для извлечения file_id из JavaScript-кода
#         file_id_match = re.search(r'"([a-zA-Z0-9_-]{25,})",true,true,false\);', driver.page_source)
#         file_id = file_id_match.group(1) if file_id_match else None
#
#         if file_id:
#             # Задайте путь, по которому вы хотите сохранить файл
#             download_path = f'./{file_name}'

#             # Скачивание файла
#             gdown.download(f'https://drive.google.com/uc?id={file_id}', download_path, quiet=False)
#             print(f'Файл "{file_name}" успешно скачан.')
#         else:
#             print(f'Не удалось найти file_id для файла: {file_name}')
#
# finally:
#     # Закройте браузер после использования
#     driver.quit()

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

file_id = "1jq4m7oI5215WeO19ISh-_7cyvPZlcaQk"
destination = "./15.11.2023.xlsx"

download_file_from_google_drive(file_id, destination)

