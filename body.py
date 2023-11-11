from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import openpyxl

import Links
def download_file_from_drive(drive, file_name, folder_id):
    # Ищем файл в указанной папке по имени
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and title = '{file_name}'"}).GetList()

    if file_list:
        # Скачиваем файл
        file_id = file_list[0]['id']
        downloaded_file = drive.CreateFile({'id': file_id})
        downloaded_file.GetContentFile(file_name)

def parse_excel(file_path):
    workbook = openpyxl.load_workbook(file_path)
    result = {}

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        date, lesson, occupancy, *schedule_data = sheet[1][0].value.split()
        result[sheet_name] = {'date': date, 'lesson': lesson, 'occupancy': occupancy, 'schedule_data': []}

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0]:  # Если есть номер аудитории
                room, *group_teacher = row
                group, teacher = group_teacher[0] if group_teacher else (None, None)
                result[sheet_name]['schedule_data'].append({'room': room, 'group': group, 'teacher': teacher})

    # Закрываем файл
    workbook.close()

    return result

def main():
    # Авторизация в Google Drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # ID папки на Google Drive
    folder_id = Links.folder_id

    # Ввод даты (пока что в формате 'dd-mm-yyyy')
    date_input = input("Введите дату (в формате 'dd-mm-yyyy'): ")

    # Формируем имя файла
    file_name = f"{date_input}.xlsx"

    # Скачиваем файл из Google Drive
    download_file_from_drive(drive, file_name, folder_id)

    # Парсим скачанный файл
    data = parse_excel(file_name)

    # Вывод результата
    for sheet_name, sheet_data in data.items():
        print(f"Лист: {sheet_name}")
        print(f"Дата: {sheet_data['date']}")
        print(f"Пара: {sheet_data['lesson']}")
        print(f"Корпус: {sheet_data['occupancy']}")
        print("Расписание:")
        for schedule_item in sheet_data['schedule_data']:
            print(f"  Аудитория: {schedule_item['room']}, Группа: {schedule_item['group']}, Преподаватель: {schedule_item['teacher']}")
        print("\n")

if __name__ == "__main__":
    main()
