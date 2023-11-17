import asyncio
import json
import logging
import sys

from aiogram import Router

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove, KeyboardButton
import Links_tg
from aiogram.filters import Filter
from aiogram.types import Message

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
    await message.answer("Привет. Я помогу посмотреть планшетку РКСИ.\n"
                         "Для поиска /search, для помощи /help, для отмены операции /cancel")


@router.message(Command("search"))
async def cmd_search(message: types.Message):
    kb = [
        [KeyboardButton(text="Дата")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, input_field_placeholder="нажми кнопку внизу")
    await message.answer("Для навигации используй кнопки ниже.\n\n",
                         reply_markup=keyboard)


@router.message(Command("help"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer("Напишите на +79895099849", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(Command("cancel"))
async def help_cmd(message: types.Message, state: FSMContext):
    await message.answer("Операция отмена, закругляемся...", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.lower() == "дата")
async def date_command(message: types.Message, state: FSMContext) -> None:
    with open('../files_data.json', 'r') as f:
        data = json.load(f)

    keyboard = []

    for key in data.keys():
        button = [KeyboardButton(text=key)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard, input_field_placeholder="выбери кнопку внизу")

    await message.answer("Выберите дату:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_date)


@router.message(DateState.waiting_for_date)
async def handle_date_choice(message: types.Message, state: FSMContext):
    selected_date = message.text

    with open('../files_data.json', 'r') as f:
        dates_data = json.load(f)

    if selected_date in dates_data:
        await state.update_data(selected_date=selected_date)
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
    await message.answer(f"Введите {data_type.lower()}:\n\n"
                         f"Для справки:\n"
                         "   1. Группу вводить вида ИС-33, 2-ИС-3, ПОКС-45w\n"
                         "   2. Преподавателя вводить вида Галушкина Д.Е.\n"
                         "   3. Кабинет вводить вида 306, 110а, Общ1-3\n\n", reply_markup=ReplyKeyboardRemove())
    await state.set_state(DateState.waiting_for_value)


@router.message(DateState.waiting_for_value)
async def handle_value_input(message: types.Message, state: FSMContext):
    value = message.text
    await state.update_data(value=value)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Все пары'), KeyboardButton(text='Конкретная')]
    ],  input_field_placeholder="выбери кнопку внизу")
    await message.answer("Выберите 'Все пары' или 'Конкретная':", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_action)


class MyFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text


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
            f"Вы выбрали {data['data_type']} {data['value']} за {data['selected_date']} и все пары.",
            reply_markup=ReplyKeyboardRemove())

        for num_para, items in json_file.items():
            await state.update_data(num_para=num_para)
            data = await state.get_data()

            if str(data['num_para']) in json_file:
                if data['data_type'] == "Группа":
                    await handle_group_type(data, message, json_file, lst_group, lst_room, lst_teacher)
                elif data['data_type'] == "Кабинет":
                    await handle_room_type(data, message, json_file, lst_group, lst_room, lst_teacher)
                elif data['data_type'] == "Преподаватель":
                    await handle_teacher_type(data, message, json_file, lst_group, lst_room, lst_teacher)
                else:
                    await message.answer("Неизвестный тип данных")

            await state.update_data(num_para=None)  # Сброс данных о паре

    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    except json.JSONDecodeError:
        await message.answer(f"Ошибка при чтении файла")
    finally:
        await state.clear()

    await message.answer("💯💯💯 Все пары обработаны", reply_markup=ReplyKeyboardRemove())


@router.message(DateState.waiting_for_action, F.text.lower() == 'конкретная')
async def handle_concrete_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    with open('../data_concretn.json', 'r') as f:
        data_concretn = json.load(f)

    keyboard = []

    for item in data_concretn.get(data['selected_date'], []):
        button = [KeyboardButton(text=item)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard,  input_field_placeholder="выбери кнопку внизу")

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
                await handle_group_type(data, message, json_file, lst_group, lst_room, lst_teacher)
            elif data['data_type'] == "Кабинет":
                await handle_room_type(data, message, json_file, lst_group, lst_room, lst_teacher)
            elif data['data_type'] == "Преподаватель":
                await handle_teacher_type(data, message, json_file, lst_group, lst_room, lst_teacher)
            else:
                await message.answer("Неизвестный тип данных")
        else:
            await message.answer("Данные для выбранной пары не найдены")
    except FileNotFoundError:
        await message.answer(f"Файл не найден")
    finally:
        await state.clear()


async def handle_group_type(data, message, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_group_item(data, message, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
    else:
        found = await handle_group_item(data, message, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)

    if not found_items:
        await message.answer(
            f"❌ Выбранная {data['data_type']} {data['value']} не найдена на {str(data['num_para']).replace('пара', 'паре')}.",
            reply_markup=ReplyKeyboardRemove())


async def handle_group_item(data, message, item, lst_group, lst_room, lst_teacher):
    found = False
    for group_key in lst_group:
        if item.get(group_key) is not None and item.get(group_key) == data['value']:
            await message.answer(
                f"✅ {data['data_type']} {data['value']} за {data['selected_date']} и {data['num_para']}.\n\n"
                f"  Кабинет: {item.get(lst_room[lst_group.index(group_key)])}\n"
                f"  Группа: {item.get(group_key)}\n"
                f"  Преподаватель: {item.get(lst_teacher[lst_group.index(group_key)])}\n",
                reply_markup=ReplyKeyboardRemove())
            found = True

    return found


async def handle_room_type(data, message, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_room_item(data, message, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
    else:
        found = await handle_room_item(data, message, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)

    if not found_items:
        await message.answer(
            f"❌ Выбранный {data['data_type']} {data['value']} не найден на {str(data['num_para']).replace('пара', 'паре')}.",
            reply_markup=ReplyKeyboardRemove())


async def handle_room_item(data, message, item, lst_group, lst_room, lst_teacher):
    found_items = []
    for room_key in lst_room:
        if item.get(room_key) is not None and item.get(room_key) == data['value']:
            await message.answer(
                f"✅ {data['data_type']} {data['value']} за {data['selected_date']} и {data['num_para']}.\n\n"
                f"  Кабинет: {item.get(room_key)}\n"
                f"  Группа: {item.get(lst_group[lst_room.index(room_key)])}\n"
                f"  Преподаватель: {item.get(lst_teacher[lst_room.index(room_key)])}\n",
                reply_markup=ReplyKeyboardRemove())
            found_items.append(True)

    return found_items


async def handle_teacher_type(data, message, json_file, lst_group, lst_room, lst_teacher):
    found_items = []
    if isinstance(json_file[data['num_para']], list):
        for item in json_file[data['num_para']]:
            found = await handle_teacher_item(data, message, item, lst_group, lst_room, lst_teacher)
            if found:
                found_items.append(found)
    else:
        found = await handle_teacher_item(data, message, json_file[data['num_para']], lst_group, lst_room, lst_teacher)
        if found:
            found_items.append(found)

    if not found_items:
        await message.answer(
            f"❌ Выбранный {data['data_type']} {data['value']} не найден на {str(data['num_para']).replace('пара', 'паре')}.",
            reply_markup=ReplyKeyboardRemove())


async def handle_teacher_item(data, message, item, lst_group, lst_room, lst_teacher):
    found_items = []
    for teacher_key in lst_teacher:
        if item.get(teacher_key) is not None and item.get(teacher_key) == data['value']:
            await message.answer(
                f"✅ {data['data_type']} {data['value']} за {data['selected_date']} и {data['num_para']}.\n\n"
                f"  Кабинет: {item.get(lst_room[lst_teacher.index(teacher_key)])}\n"
                f"  Группа: {item.get(lst_group[lst_teacher.index(teacher_key)])}\n"
                f"  Преподаватель: {item.get(teacher_key)}\n",
                reply_markup=ReplyKeyboardRemove())
            found_items.append(True)

    return found_items


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
