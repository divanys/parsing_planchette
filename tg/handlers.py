import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import Links_tg

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=Links_tg.api_tg)
# Диспетчер
dp = Dispatcher()


class DateState(StatesGroup):
    waiting_for_date = State()
    waiting_for_data_type = State()
    waiting_for_value = State()
    waiting_for_action = State()
    waiting_for_concrete = State()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Дата")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer("Привет. Я помогу посмотреть планшетку РКСИ.\n"
                         "Для навигации используй кнопки ниже.", reply_markup=keyboard)


@dp.message(F.text.lower() == "дата")
async def date_command(message: types.Message, state: FSMContext):
    with open('../files_data.json', 'r') as f:
        data = json.load(f)

    keyboard = []

    for key in data.keys():
        button = [types.KeyboardButton(text=key)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard)

    await message.answer("Выберите дату:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_date)


@dp.message(state=DateState.waiting_for_date)
async def handle_date_choice(message: types.Message, state: FSMContext):
    selected_date = message.text

    with open('../files_data.json', 'r') as f:
        dates_data = json.load(f)

    if selected_date in dates_data:
        await state.update_data(selected_date=selected_date)
        keyboard = types.ReplyKeyboardMarkup(keyboard=[
            [types.KeyboardButton(text="Кабинет"), types.KeyboardButton(text='Группа'), types.KeyboardButton(text='Преподаватель')]
        ])
        await message.answer("Выберите тип данных для поиска:", reply_markup=keyboard)
        await state.set_state(DateState.waiting_for_data_type)
    else:
        await message.answer("Неверная дата. Выберите дату из списка.")


@dp.message(state=DateState.waiting_for_data_type)
async def handle_data_type_choice(message: types.Message, state: FSMContext):
    data_type = message.text
    await state.update_data(data_type=data_type)
    await message.answer(f"Введите {data_type.lower()}:")
    await state.set_state(DateState.waiting_for_value)


@dp.message(state=DateState.waiting_for_value)
async def handle_value_input(message: types.Message, state: FSMContext):
    value = message.text
    await state.update_data(value=value)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text='Все пары'), types.KeyboardButton(text='Конкретная')]
    ])
    await message.answer("Выберите 'Все пары' или 'Конкретная':", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_action)


@dp.message(state=DateState.waiting_for_action, text='Все пары')
async def handle_all_classes_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"Вы выбрали {data['data_type']} {data['value']} за {data['selected_date']} и все пары.")
    await state.clear()


@dp.message(state=DateState.waiting_for_action, text='Конкретная')
async def handle_concrete_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    with open('../data_concretn.json', 'r') as f:
        data_concretn = json.load(f)

    keyboard = []

    for item in data_concretn.get(data['selected_date'], []):
        button = [types.KeyboardButton(text=item)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard)

    await message.answer("Выберите конкретную пару:", reply_markup=keyboard)
    await state.set_state(DateState.waiting_for_concrete)


@dp.message(state=DateState.waiting_for_concrete)
async def handle_concrete_choice(message: types.Message, state: FSMContext):
    concrete_value = message.text
    data = await state.get_data()
    await message.answer(f"Вы выбрали конкретную пару {concrete_value} за {data['selected_date']}.")
    await state.clear()

    # Сбрасываем состояние и предлагаем выбрать новую дату
    with open('../files_data.json', 'r') as f:
        dates_data = json.load(f)

    keyboard = []

    for date_str in dates_data.keys():
        button = [types.KeyboardButton(text=date_str)]
        keyboard.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard)

    await message.answer("Выберите дату:", reply_markup=keyboard)


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Напиши на +79895099849")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
