import json
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import Links_tg

storage = MemoryStorage()
chatbot = Bot(token=Links_tg.api_tg)
dp = Dispatcher(chatbot, storage=storage)

with open('../files_data.json', 'r') as file:
    dates_data = json.load(file)

with open('../data_concretn.json', 'r') as file:
    data_concretn = json.load(file)


class DateState(StatesGroup):
    waiting_for_date = State()
    waiting_for_data_type = State()
    waiting_for_value = State()
    waiting_for_action = State()
    waiting_for_concrete = State()


@dp.message_handler(commands=['start'])
async def start_cmd(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Дата'))
    await message.answer("Привет. Я помогу посмотреть планшетку РКСИ.\n"
                         "Для навигации используй кнопки ниже.", reply_markup=markup)


@dp.message_handler(Text(equals='Дата'))
async def date_handler(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for date_str in dates_data.keys():
        markup.add(KeyboardButton(date_str))

    await message.answer("Выберите дату:", reply_markup=markup)
    await DateState.waiting_for_date.set()


@dp.message_handler(state=DateState.waiting_for_date)
async def handle_date_choice(message: Message, state: FSMContext):
    selected_date = message.text
    if selected_date in dates_data:
        await state.update_data(selected_date=selected_date)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton('Кабинет'), KeyboardButton('Группа'), KeyboardButton('Преподаватель'))
        await message.answer("Выберите тип данных для поиска:", reply_markup=markup)
        await DateState.waiting_for_data_type.set()
    else:
        await message.answer("Неверная дата. Выберите дату из списка.")


@dp.message_handler(state=DateState.waiting_for_data_type)
async def handle_data_type_choice(message: Message, state: FSMContext):
    data_type = message.text
    await state.update_data(data_type=data_type)
    await message.answer(f"Введите {data_type.lower()}:")
    await DateState.waiting_for_value.set()


@dp.message_handler(state=DateState.waiting_for_value)
async def handle_value_input(message: Message, state: FSMContext):
    value = message.text
    await state.update_data(value=value)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Все пары'), KeyboardButton('Конкретная'))
    await message.answer("Выберите 'Все пары' или 'Конкретная':", reply_markup=markup)
    await DateState.waiting_for_action.set()


@dp.message_handler(state=DateState.waiting_for_action, text='Все пары')
async def handle_all_classes_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"Вы выбрали {data['data_type']} {data['value']} за {data['selected_date']} и все пары.")
    await state.finish()

@dp.message_handler(state=DateState.waiting_for_action, text='Конкретная')
async def handle_concrete_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in data_concretn.get(data['selected_date'], []):
        markup.add(KeyboardButton(item))

    await message.answer("Выберите конкретную пару:", reply_markup=markup)
    await DateState.waiting_for_concrete.set()

@dp.message_handler(state=DateState.waiting_for_concrete)
async def handle_concrete_choice(message: Message, state: FSMContext):
    concrete_value = message.text
    data = await state.get_data()
    await message.answer(f"Вы выбрали конкретную пару {concrete_value} за {data['selected_date']}.")
    await state.finish()

    # Сбрасываем состояние и предлагаем выбрать новую дату
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for date_str in dates_data.keys():
        markup.add(KeyboardButton(date_str))

    await message.answer("Выберите дату:", reply_markup=markup)


@dp.message_handler(commands=['help'])
async def help_cmd(message: Message):
    await message.answer("Напиши на +79895099849")


if __name__ == "__main__":
    executor.start_polling(dp)
