import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, date

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


class DateStateMainBeach(StatesGroup):  # для общения с главным пляжем, ахвзахвза
    waiting_for_first = State()
    waiting_for_second = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Здравствуй. Я помогу посмотреть планшеточку РКСИ.\n\n"
                         "🔎 <b>Для поиска</b> /search\n\n"
                         "Для отмены операции /cancel\n"
                         "Для помощи /help\n"
                         "Для удаления шаблона /remove_pattern\n\n"
                         "⚠ <b>Для просмотра правил</b> /rules\n\n",
                         reply_markup=ReplyKeyboardRemove())


@router.message(Command("gussi_pussi_i_am_very_glavnii"))
async def cmd_main_beach(message: types.Message, state: FSMContext):
    if message.from_user.id == Links_tg.main_beach:
        kb = [
            [
                KeyboardButton(text="0"),
                KeyboardButton(text="1"),
                KeyboardButton(text="2"),
                KeyboardButton(text="3"),
                KeyboardButton(text="4")
            ]
        ]

        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, input_field_placeholder="ебанько, кнопки есть")

        await message.answer(f'Привет, main beach ин этот телеграмм, ес.\n'
                             f'Поиграем в бога РКСИ?)\n\n'
                             f'0 - сводка на сегодня\n'
                             f'1 - {"установить сокращёнку сегодня 🥳" if Links_tg.reduce_day == False else "убрать сокращёнку сегодня 👿"}\n'
                             f'2 - {"установить сокращёнку завтра 🥳🥳" if Links_tg.reduce_day_tomorrow == False else "убрать сокращёнку завтра 👿"}\n'
                             f'3 - разосласть всем/папищикам крутое сообщение\n'
                             '4 - /cancel\n', reply_markup=keyboard)

        await state.set_state(DateStateMainBeach.waiting_for_first)
    else:
        await message.answer("Я так не понимаю\n"
                             "🔎 Для поиска /search")


@router.message(DateStateMainBeach.waiting_for_first)
async def cmd_main_func(message: types.Message, state: FSMContext):
    what = ''

    try:
        if str(message.text) == '1':
            await cmd_reduce_day_today()
            what = 'cmd_reduce_day_today'
        elif str(message.text) == '2':
            await cmd_reduce_day_tomorrow()
            what = 'cmd_reduce_day_tomorrow'
        elif str(message.text) == '3':
            await cmd_message()
            what = 'cmd_message'
        elif str(message.text) == '4':
            await message.answer("Операция отмена, закругляемся...\n")
            await state.clear()
            what = 'cancel_cmd'

        elif str(message.text) == '0':
            what = 'сводка че'
            await message.answer(f'Сокращёнка сегодня: {Links_tg.reduce_day}\n'
                                 f'Сокращёнка завтра: {Links_tg.reduce_day_tomorrow}\n')

        await message.answer(f'Была выполнена команда {what}\n'
                             f'/gussi_pussi_i_am_very_glavnii\n'
                             f'/search\n',
                             reply_markup=ReplyKeyboardRemove())

    except:
        e = sys.exc_info()[1]
        # print(e.args[0])
        await message.answer(f'Была выполнена команда {what} и случилась ошибка {e.args[0]}\n'
                             f'Планируешь делать чёт?)\n'
                             f'/gussi_pussi_i_am_very_glavnii\n'
                             f'/search\n',
                             reply_markup=ReplyKeyboardRemove())
    await state.clear()

    # await state.set_state(DateStateMainBeach.waiting_for_second)


# global reduce_day

async def cmd_reduce_day_today():
    if not Links_tg.reduce_day:
        Links_tg.reduce_day = True
    else:
        Links_tg.reduce_day = False


async def cmd_reduce_day_tomorrow():
    if not Links_tg.reduce_day_tomorrow:
        Links_tg.reduce_day_tomorrow = True
    else:
        Links_tg.reduce_day_tomorrow = False


async def cmd_message():
    pass


# async def cmd_reduce_day_today(message: types.Message, state: FSMContext):
#     pass

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
async def cancel_cmd(message: types.Message, state: FSMContext):
    await message.answer("Операция отмена, закругляемся...\n"
                         "🔎 Для поиска /search", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.lower() == "искать вручную")
async def date_command(message: types.Message, state: FSMContext) -> None:
    with open('files_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # просим пользователя выбрать дату, выводя из имеющихся
    keyboard = [[KeyboardButton(text=str(key).replace(".xlsx", ""))] for key in data.keys()]

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder="выберите кнопку внизу")

    await message.answer("Выберите дату:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_date)


@router.message(DateState.waiting_for_date)
async def handle_date_choice(message: types.Message, state: FSMContext):
    selected_date = message.text

    with open('files_data.json', 'r', encoding='utf-8') as f:
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
        await message.answer("⚠ Неверная дата. Выберите дату из кнопок ниже.")


@router.message(DateState.waiting_for_data_type)
async def handle_data_type_choice(message: types.Message, state: FSMContext):
    data_type = message.text
    if str(data_type).lower() in [
        'кабинет',
        'группа',
        'преподаватель'
    ]:
        await state.update_data(data_type=data_type)
        await message.answer(f"Введите {str(data_type.lower()).replace('ппа', 'ппу').replace('атель', 'ателя')}:\n\n"
                             f"Для справки:\n"
                             "   1. Если выбрали группу, вводить её вида ИС-33 или 2-ИС-3 или ПОКС-45w\n"
                             "   2. Если выбрали преподавателя, вводить его вида Галушкина Д.Е.\n"
                             "   3. Если выбрали кабинет, вводить его вида 306 или 110а или Общ1-3\n\n"
                             "⚠ Вводите данные только для выбранного значения! ", reply_markup=ReplyKeyboardRemove())
        await state.set_state(DateState.waiting_for_value)
    else:
        await message.answer("⚠ Неверный тип данных для поиска. Выберите вариант из кнопок ниже.")


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

    file_path = f'all_planchette/{str(data["selected_date"]).replace(".xlsx", "")}.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_file = json.load(f)

        message_all = ""

        for num_para, items in json_file.items():
            await state.update_data(num_para=num_para)
            data = await state.get_data()

            if str(data['num_para']) in json_file:
                if data['data_type'].lower():
                    weekday = datetime.strptime(str(data["selected_date"]).rsplit('.', 1)[0], "%d.%m.%Y").weekday()
                    message_all += await handle_type(data, data['data_type'], data['value'], json_file, weekday)
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
    with open('data_concretn.json', 'r', encoding='utf-8') as f:
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

    file_path = f'all_planchette/{str(data["selected_date"]).replace(".xlsx", "")}.json'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_file = json.load(f)

        if str(data['num_para']) in json_file:
            if data['data_type'].lower():
                weekday = datetime.strptime(str(data["selected_date"]).rsplit('.', 1)[0], "%d.%m.%Y").weekday()
                messages = await handle_type(data, data['data_type'], data['value'], json_file, weekday)
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


async def handle_type(data, data_type, data_value, json_file, weekday):
    found_items = []
    message_all = ""

    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_item(data, data_type, data_value, item, weekday)
            if found:
                found_items.append(found)
                message_all += found

    if not found_items:
        message_all += \
            f"❌ {str(data['num_para'])}: расписание отстутсвует.\n\n"

    return message_all


async def handle_item(data, data_type, data_value, file, weekday):
    message_all = ""
    data_type = data_type.lower()
    key_lst = ['room', 'group', 'teacher']

    if ((Links_tg.reduce_day is True and weekday == datetime.now().date().weekday())
            or (Links_tg.reduce_day_tomorrow is True and weekday == 6)):
        with open('shedule/reduce_day.json', 'r', encoding='utf-8') as f:
            what_day = json.load(f)
    elif weekday == 0 or weekday == 6:
        with open('shedule/monday.json', 'r', encoding='utf-8') as f:
            what_day = json.load(f)
    elif weekday == 3:
        with open('shedule/thursday.json', 'r', encoding='utf-8') as f:
            what_day = json.load(f)
    elif weekday != 3 and weekday != 0:
        with open('shedule/ordinary_day.json', 'r', encoding='utf-8') as f:
            what_day = json.load(f)

    if data_type == 'кабинет':
        key = key_lst[0]
        if file.get(key) is not None and str(data_value) == str(file.get(key)):
            if str(file.get(key_lst[1])).upper() != 'ОТСУТСТВУЕТ' and str(
                    file.get(key_lst[2])).title() != 'ОТСУТСТВУЕТ':
                message_all += \
                    f"✅ {data['num_para']}.\n" \
                    f"  Время: {what_day[data['num_para']]}\n" \
                    f"  Кабинет: {file.get(key_lst[0])}\n" \
                    f"  Группа: {str(file.get(key_lst[1])).upper()}\n" \
                    f"  Преподаватель: {str(file.get(key_lst[2])).title()}\n\n"
            else:
                message_all += \
                    f"❌ {data['num_para']}.\n" \
                    f"  Кабинет пуст!\n\n"

    if data_type == 'группа':
        key = key_lst[1]
        if file.get(key) is not None and str(data_value) in file.get(key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Время: {what_day[data['num_para']]}\n" \
                f"  Кабинет: {file.get(key_lst[0])}\n" \
                f"  Группа: {str(file.get(key_lst[1])).upper()}\n" \
                f"  Преподаватель: {str(file.get(key_lst[2])).title()}\n\n"

    if data_type == 'преподаватель':
        key = key_lst[2]
        if file.get(key) is not None and str(data_value) in file.get(key):
            message_all += \
                f"✅ {data['num_para']}.\n" \
                f"  Время: {what_day[data['num_para']]}\n" \
                f"  Кабинет: {file.get(key_lst[0])}\n" \
                f"  Группа: {str(file.get(key_lst[1])).upper() if str(file.get(key_lst[1])).upper() != 'ОТСУТСТВУЕТ' else 'Отсутствует'}\n" \
                f"  Преподаватель: {str(file.get(key_lst[2])).title()}\n\n"

    return message_all


class DataStateConst(StatesGroup):
    waiting_for_reg_pattern = State()
    waiting_for_data_type_const = State()
    waiting_for_value_const = State()


@router.message(F.text.lower() == "использовать шаблон")
async def pattern_reg_or_print(message: types.Message, state: FSMContext) -> None:
    with open('tg/pattern_for_user.json',
              'r', encoding='utf-8') as f:
        data_user = json.load(f)

    current_date = datetime.now()
    weekday = current_date.weekday()

    if weekday == 6:
        current_date += timedelta(days=1)
    #    current_date = date(2023, 1, 12)

    file_path = f'all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    user_id_for_pattern = str(message.from_user.id)
    try:
        with open(file_path, 'r') as f:
            json_file = json.load(f)

        if user_id_for_pattern in data_user:
            user_data = data_user[user_id_for_pattern]

            message_all = ""
            for num_para, items in json_file.items():
                await state.update_data(num_para=num_para)
                data = await state.get_data()
                for item in user_data:
                    type_for_search = item.get("type")
                    value_for_search = item.get("value")

                    if str(data['num_para']) in json_file:
                        if type_for_search.lower():
                            message_all += await handle_type(data, type_for_search, value_for_search, json_file,
                                                             weekday)

            if message_all != "":
                await message.answer(message_all, reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Пар нет!",
                                     reply_markup=ReplyKeyboardRemove())
            await state.clear()
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
    if str(type_value).lower() in [
        'кабинет',
        'группа',
        'преподаватель'
    ]:
        await state.update_data(type_value=type_value)
        await message.answer(f"Введите {str(type_value.lower()).replace('ппа', 'ппу').replace('атель', 'ателя')}:\n\n"
                             f"Для справки:\n"
                             "   1. Если выбрали группу, вводить её вида ИС-33 или 2-ИС-3 или ПОКС-45w\n"
                             "   2. Если выбрали преподавателя, вводить его вида Галушкина Д.Е.\n"
                             "   3. Если выбрали кабинет, вводить его вида 306 или 110а или Общ1-3\n\n"
                             "⚠ Вводите данные только для выбранного значения!", reply_markup=ReplyKeyboardRemove())
        await state.set_state(DataStateConst.waiting_for_value_const)
    else:
        await message.answer("⚠ Неверный тип данных для поиска. Выберите вариант из кнопок ниже.")


@router.message(DataStateConst.waiting_for_value_const)
async def final_reg_const(message: types.Message, state: FSMContext):
    data = await state.get_data()

    id_value = str(data["id_user_const"])
    type_value = data["type_value"]
    value_value = str(message.text).lower()

    file_path1 = 'tg/pattern_for_user.json'

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

    current_date = datetime.now()
    weekday = current_date.weekday()
    #
    if weekday == 6:
        current_date += timedelta(days=1)

    # current_date = date(2023, 1, 12)

    file_path = f'all_planchette/' \
                f'{current_date.strftime("%d.%m.%Y")}.json'

    user_id_for_pattern = id_value
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_file = json.load(f)

        user_data = existing_data[user_id_for_pattern]

        message_all = ""
        for num_para, items in json_file.items():
            await state.update_data(num_para=num_para)
            data = await state.get_data()
            for item in user_data:
                type_for_search = item.get("type")
                value_for_search = item.get("value")

                if str(data['num_para']) in json_file:
                    if type_for_search.lower():
                        message_all += await handle_type(data, type_for_search, value_for_search, json_file, weekday)

        if message_all != "":
            await message.answer(message_all, reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Пар нет!",
                                 reply_markup=ReplyKeyboardRemove())

    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")

    await message.answer("🔎 Для поиска /search\n\nУдалить шаблон /remove_pattern\n")
    await state.clear()


@router.message(Command('remove_pattern'))
async def remove_pattern(message: types.Message):
    user_id = str(message.from_user.id)
    file_path = 'tg/pattern_for_user.json'

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
                         "\nИспользуя шаблон, вы сможете просматривать расписание за <b>весь текущий день</b> (или <b>понедельник</b>, если используете в воскресенье).\n\n"
                         "Удалить шаблон /remove_pattern"
                         "\nВы можете <b>создать новый</b> шаблон после удаления)",
                         reply_markup=ReplyKeyboardRemove())


# спешл фор зе бьютифул вумэн, вхич ис бэст оф зе бэст
@router.message(Command('boolean_balagan_today'))
async def print_boolean_balagan(message: types.Message):
    current_date = datetime.now()
    weekday = current_date.weekday()

    if weekday == 6:
        current_date += timedelta(days=1)

    file_path = f'all_planchette/' \
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
    current_date = datetime.now()
    current_date += timedelta(days=1)
    weekday = current_date.weekday()

    if weekday == 6:
        current_date += timedelta(days=1)

    file_path = f'all_planchette/' \
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
    bot = Bot(token=Links_tg.api_tg, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
