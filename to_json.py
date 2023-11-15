import os
import json
from openpyxl import load_workbook
from datetime import datetime


def parse_and_convert_to_json(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory, filename)
            print("Обрабатываем файл:", file_path)
            parse_xlsx_and_convert_to_json(file_path, directory, filename)


def parse_xlsx_and_convert_to_json(file_path, output_directory, filename):
    wb = load_workbook(file_path)
    json_data = {}

    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        json_data[sheet_name] = []

        for row in range(2, sheet.max_row + 1):
            data_entry = {}
            data_entry["header_date"] = str(sheet.cell(row=1, column=1).value)
            data_entry["header_pair"] = str(sheet.cell(row=1, column=2).value)

            room_a = str(sheet.cell(row=row, column=1).value)
            room_d = str(sheet.cell(row=row, column=4).value)
            group_b = str(sheet.cell(row=row, column=2).value)
            group_e = str(sheet.cell(row=row, column=5).value)
            teacher_c = str(sheet.cell(row=row, column=3).value)
            teacher_f = str(sheet.cell(row=row, column=6).value)

            if room_a:
                entry = {"header_date": data_entry["header_date"], "header_pair": data_entry["header_pair"],
                         "room_a": room_a, "group_b": group_b, "teacher_c": teacher_c}
                json_data[sheet_name].append(entry)

            if room_d:
                entry = {"header_date": data_entry["header_date"], "header_pair": data_entry["header_pair"],
                         "room_d": room_d, "group_e": group_e, "teacher_f": teacher_f}
                json_data[sheet_name].append(entry)

    json_filename = f"{os.path.splitext(filename)[0]}.json"
    json_filepath = os.path.join(output_directory, json_filename)

    with open(json_filepath, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


directory = "all_planchette"
parse_and_convert_to_json(directory)