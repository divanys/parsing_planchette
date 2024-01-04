import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Router, Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, KeyboardButton

import Links_tg

# включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# объект бота
router = Router(name=__name__)


class DateState(StatesGroup):  # для общения пользователя в процессе "Искать вручную"
    waiting_for_date = State()
    waiting_for_data_type = State()
    waiting_for_value = State()
    waiting_for_action = State()
    waiting_for_concrete = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Здравствуй. Я помогу посмотреть планшеточку РКСИ.\n\n"
                         "🔎 <b>Для поиска</b> /search\n\n"
                         "Для отмены операции /cancel\n"
                         "Для помощи /help\n"
                         "Для удаления шаблона /remove_pattern\n\n"
                         "⚠ <b>Для просмотра правил</b> /rules\n\n",
                         reply_markup=ReplyKeyboardRemove())


@router.message(Command("search"))
async def cmd_search(message: types.Message):
    kb = [
        [KeyboardButton(text="Искать вручную"),
         KeyboardButton(text="Использовать шаблон")]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, input_field_placeholder="нажми кнопку внизу")
    await message.answer(
        "⚠ Почитать правила использования для кнопок можно /rules\n\n"
        "Для навигации используй кнопки ниже.\n",
        reply_markup=keyboard)


@router.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Напишите на +79895099849\n"
                         "🔎 Для поиска /search и дальше по кнопочкам)\n"
                         "Принимаю и требую обратной связи!", reply_markup=ReplyKeyboardRemove())


@router.message(Command("cancel"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer("Операция отмена, закругляемся...\n"
                         "🔎 Для поиска /search", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.lower() == "искать вручную")
async def date_command(message: types.Message, state: FSMContext) -> None:
    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/files_data.json', 'r') as f:
        data = json.load(f)

    # просим пользователя выбрать дату, выводя из имеющихся
    keyboard = [[KeyboardButton(text=str(key).replace(".xlsx", ""))] for key in data.keys()]

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder="выберите кнопку внизу")

    await message.answer("Выберите дату:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_date)


@router.message(DateState.waiting_for_date)
async def handle_date_choice(message: types.Message, state: FSMContext):
    selected_date = message.text

    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/files_data.json', 'r') as f:
        dates_data = json.load(f)

    if (str(selected_date) + ".xlsx") in dates_data:
        await state.update_data(selected_date=(str(selected_date) + ".xlsx"))
        keyboard = types.ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Кабинет"), KeyboardButton(text='Группа'),
             KeyboardButton(text='Преподаватель')]
        ], input_field_placeholder="выбери кнопку внизу")
        await message.answer("Выберите тип данных для поиска:", reply_markup=keyboard)
        await state.set_state(DateState.waiting_for_data_type)
    else:
        await message.answer("Неверная дата. Выберите дату из списка.")


@router.message(DateState.waiting_for_data_type)
async def handle_data_type_choice(message: types.Message, state: FSMContext):
    data_type = message.text
    await state.update_data(data_type=data_type)
    await message.answer(f"Введите {str(data_type.lower()).replace('ппа', 'ппу').replace('атель', 'ателя')}:\n\n"
                         f"Для справки:\n"
                         "   1. Если выбрали группу, вводить её вида ИС-33 или 2-ИС-3 или ПОКС-45w\n"
                         "   2. Если выбрали преподавателя, вводить его вида Галушкина Д.Е.\n"
                         "   3. Если выбрали кабинет, вводить его вида 306 или 110а или Общ1-3\n\n"
                         "⚠ Вводите данные только для выбранного значения! ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DateState.waiting_for_value)


@router.message(DateState.waiting_for_value)
async def handle_value_input(message: types.Message, state: FSMContext):
    value = message.text
    await state.update_data(value=str(value).lower())
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Все пары'), KeyboardButton(text='Конкретная')]
    ], input_field_placeholder="выбери кнопку внизу")
    await message.answer("Выберите 'Все пары' или 'Конкретная':", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_action)


@router.message(DateState.waiting_for_action, F.text.lower() == 'все пары')
async def handle_all_classes_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()

    # удалила везде эту залупу. под чем был автор, когда писал такую хуету??????????????????????????????????
    # lst_room = ["room_a", "room_d"]
    # lst_group = ["group_b", 'group_e']
    # lst_teacher = ["teacher_c", "teacher_f"]

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/{str(data["selected_date"]).replace(".xlsx", "")}.json'
    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        await message.answer(
            f"Вы выбрали {str(data['data_type']).lower().replace('ппа', 'ппу').replace('атель', 'ателя')} {str(data['value']).title()} за {str(data['selected_date']).replace('.xlsx', '')} и все пары.",
            reply_markup=ReplyKeyboardRemove())

        message_all = ""

        for num_para, items in json_file.items():
            await state.update_data(num_para=num_para)
            data = await state.get_data()

            if str(data['num_para']) in json_file:
                if data['data_type'].lower():
                    message_all += await handle_type(data, json_file)
                else:
                    message_all = "Неизвестный тип данных. Введите всё заново)\n"

            await state.update_data(num_para=None)  # Сброс данных о паре
        await message.answer(message_all, reply_markup=ReplyKeyboardRemove())


    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")
    finally:
        await state.clear()
    await message.answer("🔎 Для поиска /search")


@router.message(DateState.waiting_for_action, F.text.lower() == 'конкретная')
async def handle_concrete_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/data_concretn.json', 'r') as f:
        data_concretn = json.load(f)

    keyboard = []

    for item in data_concretn.get(data['selected_date'], []):
        button = [KeyboardButton(text=item)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder="выбери кнопку внизу")

    await message.answer("Выберите конкретную пару:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_concrete)


@router.message(DateState.waiting_for_concrete)
async def handle_concrete_choice_is(message: types.Message, state: FSMContext):
    num_para = message.text

    await state.update_data(num_para=num_para)
    data = await state.get_data()

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/{str(data["selected_date"]).replace(".xlsx", "")}.json'

    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        if str(data['num_para']) in json_file:
            if data['data_type'].lower():
                messages = await handle_type(data, json_file)
                await message.answer(messages, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Неизвестный тип данных")
        else:
            await message.answer("Данные для выбранной пары не найдены")

    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")
    finally:
        await state.clear()
    await message.answer("🔎 Для поиска /search")


async def handle_type(data, json_file):
    found_items = []
    message_all = ""

    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_item(data, item)
            if found:
                found_items.append(found)
                message_all += found

    else:
        found = await handle_item(data, json_file[data['num_para']])
        if found:
            found_items.append(found)
            message_all += found

    if not found_items:
        message_all += \
            f"❌ {str(data['num_para'])}: расписание отстутсвует.\n\n"

    return message_all


async def handle_item(data, file):
    message_all = ""
    data_type = data['data_type'].lower()
    key_lst = ['room', 'group', 'teacher']

    if data_type == 'кабинет':
        key = key_lst[0]
        if file.get(key) is not None and str(data['value']) == str(file.get(key)):
            if str(file.get(key_lst[1])).upper() != 'ОТСУТСТВУЕТ' and str(file.get(key_lst[2])).title() != 'ОТСУТСТВУЕТ':
                message_all += \
                    f"✅ {data['num_para']}.\n" \
                    f"  Кабинет: {file.get(key)}\n" \
                    f"  Группа: {str(file.get(key_lst[1])).upper()}\n" \
                    f"  Преподаватель: {str(file.get(key_lst[2])).title()}\n\n"
            else:
                message_all += \
                    f"❌ {data['num_para']}.\n" \
                    f"  Кабинет пуст!\n\n"


    if data_type == 'группа':
        key = key_lst[1]
        if file.get(key) is not None and data['value'] in file.get(key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Кабинет: {file.get(key_lst[0])}\n" \
                f"  Группа: {str(file.get(key)).upper()}\n" \
                f"  Преподаватель: {str(file.get(key_lst[2])).title()}\n\n"

    if data_type == 'преподаватель':
        key = key_lst[2]
        if file.get(key) is not None and data['value'] in file.get(key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Кабинет: {file.get(key_lst[0])}\n" \
                f"  Группа: {str(file.get(key_lst[1])).upper() if str(file.get(key_lst[1])).upper() != 'ОТСУТСТВУЕТ' else 'Отсутствует'}\n" \
                f"  Преподаватель: {str(file.get(key)).title()}\n\n"

    return message_all


async def handle_room_type(data, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    message_all = ""

    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_room_item(data, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
                message_all += found

    else:
        found = await handle_room_item(data, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)
            message_all += found

    if not found_items:
        message_all += \
            f"❌ {str(data['num_para'])}: расписание отстутсвует.\n\n"

    return message_all


async def handle_room_item(data, item, lst_group, lst_room, lst_teacher):
    message_all = ""

    for room_key in lst_room:
        if item.get(room_key) is not None and data['value'] in str(item.get(room_key)).lower() and str(
                item.get(lst_group[lst_room.index(room_key)])).title() != "Отсутствует":
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Кабинет: {item.get(room_key)}\n" \
                f"  Группа: {str(item.get(lst_group[lst_room.index(room_key)])).title()}\n" \
                f"  Преподаватель: {str(item.get(lst_teacher[lst_room.index(room_key)])).title()}\n\n"

    return message_all


async def handle_teacher_type(data, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    message_all = ""

    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_teacher_item(data, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
                message_all += found
    else:
        found = await handle_teacher_item(data, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)
            message_all += found

    if not found_items:
        message_all += \
            f"❌ {str(data['num_para'])}: расписание отстутсвует.\n\n"

    return message_all


async def handle_teacher_item(data, item, lst_group, lst_room, lst_teacher):
    message_all = ""
    for teacher_key in lst_teacher:
        if item.get(teacher_key) is not None and str(data['value']).replace('. ', '.') in item.get(teacher_key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Кабинет: {item.get(lst_room[lst_teacher.index(teacher_key)])}\n" \
                f"  Группа: {str(item.get(lst_group[lst_teacher.index(teacher_key)])).upper()}\n" \
                f"  Преподаватель: {str(item.get(teacher_key)).title()}\n\n"

    return message_all


class DataStateConst(StatesGroup):
    waiting_for_reg_pattern = State()
    waiting_for_data_type_const = State()
    waiting_for_value_const = State()


@router.message(F.text.lower() == "использовать шаблон")
async def pattern_reg_or_print(message: types.Message, state: FSMContext) -> None:
    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/tg/pattern_for_user.json',
              'r') as f:
        data_user = json.load(f)

    lst_room = ["room_a", "room_d"]
    lst_group = ["group_b", 'group_e']
    lst_teacher = ["teacher_c", "teacher_f"]

    # Получаем текущую дату
    current_date = datetime.now()

    # Получаем номер дня недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)
    weekday = current_date.weekday()

    # Если сегодня воскресенье (weekday == 6), добавляем один день
    if weekday == 6:
        current_date += timedelta(days=1)

    # Форматируем дату для использования в пути к файлу
    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    user_id_for_pattern = str(message.from_user.id)

    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        message_all = ""

        if user_id_for_pattern in data_user:
            user_data = data_user[user_id_for_pattern]

            for item in user_data:
                type_for_search = item.get("type")
                value_for_search = item.get("value")

                if type_for_search and value_for_search:
                    await message.answer(
                        f"Дата: {datetime.now().strftime('%d.%m.%Y')}\nВы выбрали {type_for_search.lower().replace('ппа', 'ппу').replace('атель', 'ателя')} {value_for_search.title()}")
                    for num_para, items in json_file.items():
                        if str(num_para) in json_file:
                            if type_for_search.lower() == "группа":
                                for group_key in lst_group:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(group_key) is not None and value_for_search.replace(' ',
                                                                                                         '') in item1.get(
                                            group_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_group.index(group_key)])}\n" \
                                                f"  Группа: {str(item1.get(group_key)).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_group.index(group_key)])).title()}\n\n"


                            elif type_for_search.lower() == "кабинет":
                                for room_key in lst_room:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(room_key) is not None and value_for_search in str(
                                                item1.get(room_key)).lower() and str(
                                            item1.get(
                                                lst_group[lst_room.index(room_key)])).title() != "Отсутствует":
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(room_key)}\n" \
                                                f"  Группа: {str(item1.get(lst_group[lst_room.index(room_key)])).title()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_room.index(room_key)])).title()}\n\n"

                            elif type_for_search.lower() == "преподаватель":
                                for teacher_key in lst_teacher:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(teacher_key) is not None and value_for_search.replace('. ',
                                                                                                           '.') in item1.get(
                                            teacher_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_teacher.index(teacher_key)])}\n" \
                                                f"  Группа: {str(item1.get(lst_group[lst_teacher.index(teacher_key)])).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(teacher_key)).title()}\n\n"
                            else:
                                await message.answer("Неизвестный тип данных")

            if message_all != "":
                await message.answer(message_all, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Вы либо допустили ошибку в написании шаблона, либо пар действительно нет.",
                                     reply_markup=ReplyKeyboardRemove())

            await message.answer("🔎 Для поиска /search")

        else:
            keyboard = types.ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="Да"), KeyboardButton(text='Нет')]],
                input_field_placeholder="выбери кнопку внизу")

            await message.answer("У вас отсутствует шаблон! Желаете создать?)", reply_markup=keyboard)
            await state.update_data(id_user_const=user_id_for_pattern)

            await state.set_state(DataStateConst.waiting_for_reg_pattern)


    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")


@router.message(DataStateConst.waiting_for_reg_pattern, F.text.lower() == 'да')
async def handle_date_choice_const(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Кабинет"), KeyboardButton(text='Группа'),
         KeyboardButton(text='Преподаватель')]
    ], input_field_placeholder="выбери кнопку внизу")
    await message.answer("Выберите тип данных для поиска:", reply_markup=keyboard)
    await state.set_state(DataStateConst.waiting_for_data_type_const)


@router.message(DataStateConst.waiting_for_data_type_const)
async def handle_data_type_choice_const(message: types.Message, state: FSMContext):
    type_value = message.text
    await state.update_data(type_value=type_value)
    await message.answer(f"Введите {str(type_value.lower()).replace('ппа', 'ппу').replace('атель', 'ателя')}:\n\n"
                         f"Для справки:\n"
                         "   1. Если выбрали группу, вводить её вида ИС-33 или 2-ИС-3 или ПОКС-45w\n"
                         "   2. Если выбрали преподавателя, вводить его вида Галушкина Д.Е.\n"
                         "   3. Если выбрали кабинет, вводить его вида 306 или 110а или Общ1-3\n\n"
                         "⚠ Вводите данные только для выбранного значения! ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DataStateConst.waiting_for_value_const)


@router.message(DataStateConst.waiting_for_value_const)
async def final_reg_const(message: types.Message, state: FSMContext):
    data = await state.get_data()

    id_value = str(data["id_user_const"])
    type_value = (data["type_value"])
    value_value = str(message.text).lower()

    file_path1 = '/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/tg/pattern_for_user.json'

    try:
        with open(file_path1, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    new_entry = {
        "type": type_value,
        "value": value_value
    }

    existing_data[id_value] = [new_entry]

    with open(file_path1, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=2)

    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/tg/pattern_for_user.json',
              'r') as f:
        data_user = json.load(f)

    lst_room = ["room_a", "room_d"]
    lst_group = ["group_b", 'group_e']
    lst_teacher = ["teacher_c", "teacher_f"]

    # Получаем текущую дату
    current_date = datetime.now()

    # Получаем номер дня недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)
    weekday = current_date.weekday()

    # Если сегодня воскресенье (weekday == 6), добавляем один день
    if weekday == 6:
        current_date += timedelta(days=1)

    # Форматируем дату для использования в пути к файлу
    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    user_id_for_pattern = id_value

    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        message_all = ""

        if user_id_for_pattern in data_user:
            user_data = data_user[user_id_for_pattern]

            for item in user_data:
                type_for_search = item.get("type")
                value_for_search = item.get("value")

                if type_for_search and value_for_search:
                    await message.answer(
                        f"Дата: {datetime.now().strftime('%d.%m.%Y')}\nВы выбрали {type_for_search.lower().replace('ппа', 'ппу').replace('атель', 'ателя')} {value_for_search.title()}")
                    for num_para, items in json_file.items():
                        if str(num_para) in json_file:
                            if type_for_search.lower() == "группа":
                                for group_key in lst_group:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(group_key) is not None and value_for_search in item1.get(
                                                group_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_group.index(group_key)])}\n" \
                                                f"  Группа: {str(item1.get(group_key)).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_group.index(group_key)])).title()}\n\n"

                            elif type_for_search.lower() == "кабинет":
                                for room_key in lst_room:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(room_key) is not None and value_for_search in str(
                                                item1.get(room_key)).lower() and str(
                                            item1.get(
                                                lst_group[lst_room.index(room_key)])).title() != "Отсутствует":
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(room_key)}\n" \
                                                f"  Группа: {str(item1.get(lst_group[lst_room.index(room_key)])).title()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_room.index(room_key)])).title()}\n\n"

                            elif type_for_search.lower() == "преподаватель":
                                for teacher_key in lst_teacher:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(teacher_key) is not None and value_for_search.replace('. ', '.') \
                                                in item1.get(teacher_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_teacher.index(teacher_key)])}\n" \
                                                f"  Группа: {str(item1.get(lst_group[lst_teacher.index(teacher_key)])).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(teacher_key)).title()}\n\n"
                            else:
                                await message.answer("Неизвестный тип данных")

            if message_all != "":
                await message.answer(message_all, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Вы либо допустили ошибку в написании шаблона, либо пар действительно нет.",
                                     reply_markup=ReplyKeyboardRemove())

    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")
    finally:
        await state.clear()

    await message.answer("🔎 Для поиска /search\n\nУдалить шаблон /remove_pattern\n")


@router.message(Command('remove_pattern'))
async def remove_pattern(message: types.Message):
    user_id = str(message.from_user.id)
    file_path = '/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/tg/pattern_for_user.json'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    if user_id in existing_data:
        del existing_data[user_id]

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=2)

        await message.answer("Шаблон успешно удален.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("У вас нет сохраненного шаблона.", reply_markup=ReplyKeyboardRemove())


@router.message(Command('rules'))
async def print_rules(message: types.Message):
    await message.answer("<b>Использование вручную:</b>"
                         "\n1. Ввести команду /search"
                         "\n2. Нажать кнопку <b>'Искать вручную'</b>"
                         "\n3. Выбрать интересующую <b>дату</b>"
                         "\n4. Выбрать интересующий <b>тип поиска</b> (Кабинет/Группа/Преподаватель)"
                         "\n5. Ввести <b>значение</b> (только одно!)"
                         "\n6. Выбрать конкретную <b>пару/все пары</b>.\n\n"
                         "<b>Использование шаблона:</b>"
                         "\n1. Ввести команду /search"
                         "\n2. Нажать кнопку <b>'Использовать шаблон'</b>"
                         "\n3. <b>Зарегистрировать</b> шаблон, если таковой отсутствует: "
                         "\n      а) Выбрать <b>'да'</b>"
                         "\n      б) Выбрать интересующий <b>тип поиска</b> (Кабинет/Группа/Преподаватель)"
                         "\n      в) Ввести <b>значение</b> (только одно!)"
                         "\n4. Если у вас уже <b>зарегистрирован</b> шаблон, то просто нажмите <b>'Использовать шаблон'</b>\n"
                         "\nИспользуя шаблон, вы сможете просматривать расписание за <b>весь текущий день</b> (или <b>понедельник</b>, если используете воскресенье).\n\n"
                         "Удалить шаблон /remove_pattern"
                         "\nВы можете <b>создать новый</b> шаблон после удаления)",
                         reply_markup=ReplyKeyboardRemove())


# спешл фор зе бьютифул вумэн, вхич ис бэст оф зе бэст
@router.message(Command('boolean_balagan_today'))
async def print_boolean_balagan(message: types.Message):
    # получаем текущую дату
    current_date = datetime.now()

    # номер дня недели (где 0 - понедельник, 1 - вторник, ..., 6 - воскресенье)
    weekday = current_date.weekday()

    # если сегодня воскресенье (weekday == 6), добавляем один день
    if weekday == 6:
        current_date += timedelta(days=1)

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    message_all = ""
    message_all = await boolean_balagan(message_all, file_path)

    if message_all != "":
        await message.answer("Балаган будэ\n\n" + str(message_all), reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Балагана не будэ",
                             reply_markup=ReplyKeyboardRemove())

    await message.answer("🔎 Для поиска /search\n")


@router.message(Command('boolean_balagan_tomorrow'))
async def print_boolean_balagan(message: types.Message):
    # получаем текущую дату и прибавляем ещё один день, потому что... томорров)
    current_date = datetime.now()
    current_date += timedelta(days=1)

    # номер дня недели (где 0 - понедельник, 1 - вторник, ..., 6 - воскресенье)
    weekday = current_date.weekday()

    # если сегодня воскресенье (weekday == 6), добавляем один день
    if weekday == 6:
        current_date += timedelta(days=1)

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    message_all = ""
    message_all = await boolean_balagan(message_all, file_path)

    if message_all != "":
        await message.answer("Балаган будэ\n\n" + str(message_all), reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Балагана не будэ",
                             reply_markup=ReplyKeyboardRemove())

    await message.answer("🔎 Для поиска /search\n")


async def boolean_balagan(message_all, file_path):
    lst_room = ["room_a", "room_d"]
    lst_group = ["group_b", 'group_e']
    lst_teacher = ["teacher_c", "teacher_f"]

    with open(file_path, 'r') as f:
        json_file = json.load(f)
        type_for_search = "Кабинет"
        value_for_search = "общ"
        if type_for_search and value_for_search:
            for num_para, items in json_file.items():
                for teacher_key in lst_teacher:
                    if str(num_para) in json_file:
                        for item1 in json_file[str(num_para)]:
                            if item1.get(teacher_key) is not None and "кошкина" in item1.get(teacher_key):
                                nums_par = str(num_para)
                                if nums_par in json_file:
                                    for item2 in json_file[nums_par]:
                                        for room_key in lst_room:
                                            if item2.get(room_key) is not None and value_for_search in str(
                                                    item2.get(room_key)).lower() and str(
                                                item2.get(
                                                    lst_group[
                                                        lst_room.index(room_key)])).title() != "Отсутствует" and str(
                                                item2.get(
                                                    lst_teacher[lst_room.index(room_key)])) != "кошкина а.а.":
                                                message_all += \
                                                    f"✅ {nums_par}.\n" \
                                                    f"  Преподаватель: {str(item2.get(lst_teacher[lst_room.index(room_key)])).title()}\n\n"
    return message_all


@router.message(DataStateConst.waiting_for_reg_pattern, F.text.lower() == 'нет')
async def handle_date_choice_const(message: types.Message):
    await message.answer("Ладно.", reply_markup=ReplyKeyboardRemove())


@router.message(F.text.lower())
async def another_data_command(message: types.Message) -> None:
    await message.answer("Я так не понимаю\n"
                         "🔎 Для поиска /search")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(token=Links_tg.api_tg, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
