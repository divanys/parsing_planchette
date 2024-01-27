import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bd import create_bd

url_site = 'https://rksi.ru/mobile_schedule'


def get_schedule_from_group(group_name):
    params = {
        'group': group_name,
        'stt': 'Показать!'
    }

    response = requests.post(url_site, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    all_p_tags = soup.find_all('p')

    for p_tag in all_p_tags:
        b_tag = p_tag.find_previous_sibling('b')

        date = b_tag.text.strip()

        pairs_info = [item.strip() for item in p_tag.stripped_strings]

        print(f"Дата: {date}")
        print("Информация о парах:")
        for pair_info in pairs_info:
            print(pair_info)

        print("\n----------------------------------------------------------\n")


def get_schedule_from_teacher(teacher_name):
    params = {
        'teacher': teacher_name,
        'stt': 'Показать!'
    }

    response = requests.post(url_site, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    all_p_tags = soup.find_all('p')

    for p_tag in all_p_tags:
        b_tag = p_tag.find_previous_sibling('b')

        date = b_tag.text.strip()

        pairs_info = [item.strip() for item in p_tag.stripped_strings]

        print(f"Дата: {date}")
        print("Информация о парах:")
        for pair_info in pairs_info:
            print(pair_info)


def get_all_teacher():
    response = requests.post(url_site)
    soup = BeautifulSoup(response.text, 'html.parser')

    tag_from_name = soup.find('select', attrs={'name': "teacher"})
    all_prepods = tag_from_name.find_all('option')
    all_prepods_text = [teacher.text for teacher in all_prepods]

    return all_prepods_text


def get_all_group():
    response = requests.post(url_site)
    soup = BeautifulSoup(response.text, 'html.parser')

    tag_from_name = soup.find('select', attrs={'name': "group"})
    all_groups = tag_from_name.find_all('option')
    all_groups_text = [group.text for group in all_groups]

    return all_groups_text


# print(len(get_all_teacher()))
# print(len(get_all_group()))

# записать в бд преподы: id препода, фио препода
# записать в бд группы: id группы, группа
# предметы: id предмета, название
# карточки расписания: id, препод-группа-предмет

# преподы: перенести список в бд
# группы: перенести список в бд
# предметы: пропарсить всех преподов -> перенести список уникальных предметов в бд (можно поделить на группы)
# чтобы узнать, какие предметы есть у препода и группы: парсинг расписания препода и выделение уникальных элементов
#                                                       -> если есть совпадение препод[предмет]-группа[предмет]
#                                                       -> сделать новую запись в карточки расписания


def get_all_lessons():
    unique_lessons = set()
    for teacher in get_all_teacher():
        params = {
            'teacher': teacher,
            'stp': 'Показать!'
        }

        response = requests.post(url_site, data=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        all_p_tags = soup.find_all('p')

        for p_tag in all_p_tags:
            b_tag = p_tag.find('b')

            if b_tag:
                unique_lessons.add(b_tag.text)

    return list(unique_lessons)


# lst_all_lessons = get_all_lessons()
# print(get_schedule_from_group("ИС-33"))

def insert_all():
    db = create_bd.SchoolDatabase()

    teachers = get_all_teacher()
    for teacher_id, teacher_name in enumerate(teachers, start=1):
        db.cursor.execute('INSERT INTO teachers (id, fullname) VALUES (?, ?)', (teacher_id, teacher_name))

    groups = get_all_group()
    for group_id, group_name in enumerate(groups, start=1):
        db.cursor.execute('INSERT INTO groups (id, name) VALUES (?, ?)', (group_id, group_name))

    lessons = get_all_lessons()
    for lesson_id, lesson_name in enumerate(lessons, start=1):
        db.cursor.execute('INSERT INTO subjects (id, name) VALUES (?, ?)', (lesson_id, lesson_name))

    db.conn.commit()
    db.close_connection()


# insert_all()


def create_subject_teacher_group():
    db = create_bd.SchoolDatabase()
    db.create_tables()

    for teacher in get_all_teacher():
        params = {
            'teacher': teacher,
            'stp': 'Показать!'
        }

        response = requests.post(url_site, data=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        all_p_tags = soup.find_all('p')

        for entry in all_p_tags:
            num_para, subject, group, room = parse_schedule_entry(str(entry))

            # Получение id препода, группы и предмета
            id_teacher = db.get_teacher_id_by_name(teacher)
            id_group = db.get_group_id_by_name(group)
            id_subject = db.get_subject_id_by_name(subject)

            # Вставка данных в таблицу cards
            db.cursor.execute('''
                INSERT INTO cards (num_para, room, id_teacher, id_group, id_subject)
                VALUES (?, ?, ?, ?, ?)
            ''', (num_para, room, id_teacher, id_group, id_subject))

    db.conn.commit()
    db.close_connection()


def get_schedule_from_teacher_teg_p(teacher_name):
    params = {
        'teacher': teacher_name,
        'stp': 'Показать!'
    }

    response = requests.post(url_site, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # all_b_tags_on_lvl_p = soup.find_all('b', recursive=False)

    all_p_tags = soup.find_all('p')
    all_p_tags_lst = []
    for p_tag in all_p_tags:
        all_p_tags_lst.append(str(p_tag))

    return all_p_tags_lst


# lst_schedule = get_schedule_from_teacher_teg_p("Сулавко А.С.")
# print(lst_schedule)

def parse_schedule_entry(entry_all):
    lst_all = []
    for entry in entry_all:
        if entry != '<p><a href="/">На сайт</a></p>':
            entry_parts = entry.split('<br/><b>')
            print("entry_parts[0]: ", entry_parts[0].strip('<p>'))

            # Получение номера пары (времени)
            num_para = entry_parts[0].strip()

            # Получение предмета
            subject_part = entry_parts[1].split('</b><br/>')
            subject = subject_part[0].strip()
            print("subject_part[0]:", subject_part[0])

            # Получение группы и аудитории
            group_and_room_part = subject_part[1].strip().split(', ауд. ')
            group = group_and_room_part[0]
            room = group_and_room_part[1].strip('</p>')
            print("group:          ", group)
            print("room:           ", room)

            print()

            lst_all.append([num_para, subject, group, room])

    return lst_all


# lst_Sulavko = parse_schedule_entry(lst_schedule)
# create_subject_teacher_group()
def get_schedule_from_teacher_teg_p1(teacher_name):
    params = {
        'teacher': teacher_name,
        'stp': 'Показать!'
    }

    response = requests.post(url_site, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    teacher_data = soup.find('h3')  # Получаем данные о преподавателе из h3 тега
    schedule_data = soup.find_all(['b', 'p', 'hr'])  # Получаем все теги b, p, hr

    return teacher_data, schedule_data


def is_date_string(input_str):
    # соответствует ли строка формату даты типа 23 января, понедельник
    date_pattern = re.compile(r'\d{1,2}\s\w+,\s\w+', re.UNICODE)
    return bool(date_pattern.match(input_str))


def parse_schedule_entry1(teacher_data, schedule_data):
    teacher_name = teacher_data.text.strip()  # Получаем ФИО препода из h3 тега
    schedule = {}  # Словарь для хранения расписания преподавателя
    year = 2024
    added_dates = set()  # Множество для отслеживания уже добавленных дат

    current_date = None
    for entry in schedule_data:
        if entry.name == 'b' and is_date_string(entry.text.strip()):  # Обработка даты
            current_date = entry.text.strip()
            if current_date not in added_dates:
                schedule[current_date] = []
                added_dates.add(current_date)
        elif entry.name == 'p' and current_date is not None:  # Обработка информации о паре
            subject_info = entry.text.strip().split(', ')
            if len(subject_info) == 4:
                time, subject, group, room = subject_info
                pair_info = {
                    "время пары": time,
                    "предмет": subject,
                    "группа": group,
                    "аудитория": room
                }
                schedule[current_date].append(pair_info)

    return schedule


# Пример использования
teacher_name = "Сулавко А.С."
teacher_data, schedule_data = get_schedule_from_teacher_teg_p1(teacher_name)
schedule = parse_schedule_entry1(teacher_data, schedule_data)

import json

# Вывод расписания в формате JSON
print(json.dumps(schedule, ensure_ascii=False, indent=2))
