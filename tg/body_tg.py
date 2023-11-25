import asyncio
import json
import logging
import sys
from datetime import datetime

from aiogram import Router

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, KeyboardButton
import Links_tg

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота

router = Router(name=__name__)


class DateState(StatesGroup):
    waiting_for_date = State()
    waiting_for_data_type = State()
    waiting_for_value = State()
    waiting_for_action = State()
    waiting_for_concrete = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет. Я помогу посмотреть планшетку РКСИ.\n\n"
                         "🔎 Для поиска /search\n"
                         "Для отмены операции /cancel\n"
                         "Для помощи /help\n"
                         "Для удаления шаблона /remove_pattern\n"
                         "Для просмотра правил /rules\n\n"
                         "Использование вручную: \n"
                         "Ввести команду /search -> Нажать кнопку 'Искать вручную' -> Выбрать интересующую дату ->"
                         " Выбрать интересующий тип для поиска -> Ввести значени -> "
                         "Выбрать конкретную пару/все пары.\n\n"
                         "Использование шаблона: \n"
                         "Ввести команду /search -> Нажать кнопку 'Использовать шаблон' ->"
                         " Зарегистрировать шаблон, если таковой отсутствует: -> Выбрать 'да' -> Выбрать тип поиска -> Ввести значение\n\n"
                         "⚠ Шаблон выводит все пары за сегодняшнюю дату.\nУдалить шаблон /remove_pattern; вы можете создать новый после удаления)",
                         reply_markup=ReplyKeyboardRemove())


@router.message(Command("search"))
async def cmd_search(message: types.Message):
    kb = [
        [KeyboardButton(text="Искать вручную"),
         KeyboardButton(text="Использовать шаблон")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, input_field_placeholder="нажми кнопку внизу")
    await message.answer(
        "Для навигации используй кнопки ниже.\n\n"
        "🍙 Объявление: Кнопка 'Использовать шаблон' готова! юзайте и наслаждайтесь)\nПочитать правила использования для кнопок можно /rules",
        reply_markup=keyboard)


@router.message(Command("help"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer("Напишите на +79895099849\n"
                         "🔎 Для поиска /search и дальше по кнопочкам)", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(Command("cancel"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer("Операция отмена, закругляемся...", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.lower() == "искать вручную")
async def date_command(message: types.Message, state: FSMContext) -> None:
    with open('/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/files_data.json', 'r') as f:
        data = json.load(f)

    keyboard = []

    for key in data.keys():
        button = [KeyboardButton(text=str(key).replace(".xlsx", ""))]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder="выбери кнопку внизу")

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

    lst_room = ["room_a", "room_d"]
    lst_group = ["group_b", 'group_e']
    lst_teacher = ["teacher_c", "teacher_f"]

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
                if data['data_type'] == "Группа":
                    message_all += await handle_group_type(data, json_file, lst_group, lst_room, lst_teacher)
                elif data['data_type'] == "Кабинет":
                    message_all += await handle_room_type(data, json_file, lst_group, lst_room, lst_teacher)
                elif data['data_type'] == "Преподаватель":
                    message_all += await handle_teacher_type(data, json_file, lst_group, lst_room, lst_teacher)
                else:
                    await message.answer("Неизвестный тип данных")

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
    lst_room = ["room_a", "room_d"]
    lst_group = ["group_b", 'group_e']
    lst_teacher = ["teacher_c", "teacher_f"]

    await state.update_data(num_para=num_para)
    data = await state.get_data()

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/{str(data["selected_date"]).replace(".xlsx", "")}.json'

    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        if str(data['num_para']) in json_file:
            if data['data_type'] == "Группа":
                messages = await handle_group_type(data, json_file, lst_group, lst_room, lst_teacher)
                await message.answer(messages, reply_markup=ReplyKeyboardRemove())
            elif data['data_type'] == "Кабинет":
                messages = await handle_room_type(data, json_file, lst_group, lst_room, lst_teacher)
                await message.answer(messages, reply_markup=ReplyKeyboardRemove())
            elif data['data_type'] == "Преподаватель":
                messages = await handle_teacher_type(data, json_file, lst_group, lst_room, lst_teacher)
                await message.answer(messages, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Неизвестный тип данных")
        else:
            await message.answer("Данные для выбранной пары не найдены")
    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    finally:
        await state.clear()
    await message.answer("🔎 Для поиска /search")


async def handle_group_type(data, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    message_all = ""

    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_group_item(data, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
                message_all += found

    else:
        found = await handle_group_item(data, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)
            message_all += found

    if not found_items:
        message_all += \
            f"❌ {str(data['num_para'])}: расписание отстутсвует.\n\n"

    return message_all


async def handle_group_item(data, item, lst_group, lst_room, lst_teacher):
    message_all = ""
    for group_key in lst_group:
        if item.get(group_key) is not None and data['value'] in item.get(group_key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Кабинет: {item.get(lst_room[lst_group.index(group_key)])}\n" \
                f"  Группа: {str(item.get(group_key)).upper()}\n" \
                f"  Преподаватель: {str(item.get(lst_teacher[lst_group.index(group_key)])).title()}\n\n"

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

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{datetime.now().strftime("%d.%m.%Y")}.json'
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
                            if type_for_search == "Группа":
                                for group_key in lst_group:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(group_key) is not None and value_for_search in item1.get(
                                                group_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_group.index(group_key)])}\n" \
                                                f"  Группа: {str(item1.get(group_key)).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_group.index(group_key)])).title()}\n\n"


                            elif type_for_search == "Кабинет":
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

                            elif type_for_search == "Преподаватель":
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
                await message.answer("Вы либо допустили ошибку в написании шаблона, либо пар действительно нет."
                                     "\nУдалить шаблон /remove_pattern\n",
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

    file_path = f'/home/divan/гетБрейнсИТолькоУдалиЯТебzУдалюСЛицаЗемли/parsing_planchette/all_planchette/' \
                f'{datetime.now().strftime("%d.%m.%Y")}.json'
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
                            if type_for_search == "Группа":
                                for group_key in lst_group:
                                    for item1 in json_file[str(num_para)]:
                                        if item1.get(group_key) is not None and value_for_search in item1.get(
                                                group_key):
                                            message_all += \
                                                f"✅ {num_para}.\n" \
                                                f"  Кабинет: {item1.get(lst_room[lst_group.index(group_key)])}\n" \
                                                f"  Группа: {str(item1.get(group_key)).upper()}\n" \
                                                f"  Преподаватель: {str(item1.get(lst_teacher[lst_group.index(group_key)])).title()}\n\n"

                            elif type_for_search == "Кабинет":
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

                            elif type_for_search == "Преподаватель":
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
                await message.answer("Вы либо допустили ошибку в написании шаблона, либо пар действительно нет."
                                     "\nУдалить шаблон /remove_pattern\n",
                                     reply_markup=ReplyKeyboardRemove())

    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")
    finally:
        await state.clear()

    await message.answer("🔎 Для поиска /search")


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
    await message.answer("Использование вручную: \n"
                         "Ввести команду /search -> Нажать кнопку 'Искать вручную' -> Выбрать интересующую дату ->"
                         " Выбрать интересующий тип для поиска -> Ввести значени -> "
                         "Выбрать конкретную пару/все пары.\n\n"
                         "Использование шаблона: \n"
                         "Ввести команду /search -> Нажать кнопку 'Использовать шаблон' ->"
                         " Зарегистрировать шаблон, если таковой отсутствует: -> Выбрать 'да' -> Выбрать тип поиска -> Ввести значение\n\n"
                         "⚠ Шаблон выводит все пары за сегодняшнюю дату.\nУдалить шаблон /remove_pattern; вы можете создать новый после удаления)",
                         reply_markup=ReplyKeyboardRemove())


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
