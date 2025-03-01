import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Настройки бота
TOKEN = "ТВОЙ_ТОКЕН_БОТА"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Подключение к базе данных
conn = sqlite3.connect("clients.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    income INTEGER,
                    topik INTEGER,
                    recommendation TEXT
                 )""")
conn.commit()

# Логирование
logging.basicConfig(level=logging.INFO)

# Кнопки
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Добавить клиента"))
keyboard.add(KeyboardButton("Посчитать баллы"))

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для расчёта баллов K-Point. Выберите действие:", reply_markup=keyboard)

# Ввод данных клиента
@dp.message_handler(lambda message: message.text == "Добавить клиента")
async def add_client(message: types.Message):
    await message.answer("Введите данные клиента в формате: Имя, возраст, доход (млн), TOPIK, рекомендация (да/нет)")

@dp.message_handler()
async def process_client(message: types.Message):
    try:
        data = message.text.split(", ")
        name, age, income, topik, recommendation = data[0], int(data[1]), int(data[2]), int(data[3]), data[4]

        cursor.execute("INSERT INTO clients (name, age, income, topik, recommendation) VALUES (?, ?, ?, ?, ?)",
                       (name, age, income, topik, recommendation))
        conn.commit()
        await message.answer(f"Клиент {name} добавлен в базу!")

    except Exception as e:
        await message.answer("Ошибка! Проверьте формат данных. Используйте: Имя, возраст, доход, TOPIK, рекомендация")

# Команда "Посчитать баллы"
@dp.message_handler(lambda message: message.text == "Посчитать баллы")
async def calculate_points(message: types.Message):
    cursor.execute("SELECT * FROM clients ORDER BY id DESC LIMIT 1")
    client = cursor.fetchone()
    
    if not client:
        await message.answer("Нет данных для расчёта.")
        return

    name, age, income, topik, recommendation = client[1], client[2], client[3], client[4], client[5]
    
    points = 0
    # Расчёт по возрасту
    if 19 <= age <= 26:
        points += 40
    elif 27 <= age <= 33:
        points += 60
    elif 34 <= age <= 40:
        points += 30
    else:
        points += 10

    # Расчёт по доходу
    if 2500 <= income < 3000:
        points += 50
    elif 3000 <= income < 3500:
        points += 65
    elif 3500 <= income < 4000:
        points += 80
    elif 4000 <= income < 4500:
        points += 95
    elif 4500 <= income < 5000:
        points += 110
    elif income >= 5000:
        points += 120

    # Расчёт по TOPIK
    if 41 <= topik <= 60:
        points += 50
    elif 61 <= topik <= 80:
        points += 80
    elif topik >= 81:
        points += 120

    # Дополнительные баллы
    if recommendation.lower() == "да":
        points += 50

    await message.answer(f"Баллы для {name}: {points}")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
