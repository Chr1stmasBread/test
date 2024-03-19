import telebot
import requests
from langdetect import detect
from TOKEN import *
import sqlite3

bot = telebot.TeleBot(TOKEN)

# Создание базы данных и таблицы пользователей
def create_database():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (user_id INTEGER PRIMARY KEY, genre TEXT, gender TEXT, universe TEXT)''')

# Функция для отправки запроса к Yandex GPT
def generate_text(genre, gender, universe, query):
    model_uri = f"gpt://{FOLDER_ID}/yandexgpt-lite"

    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "user",
                "text": f"Generate story with genre: {genre}, gender: {gender}, universe: {universe}, query: {query}"
            }
        ]
    }

    response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                             headers=headers,
                             json=data)

    if response.status_code == 200:
        text = response.json()["result"]["alternatives"][0]["message"]["text"]
        return text
    else:
        error_message = 'Invalid response received: code: {}, message: {}'.format(response.status_code, response.text)
        return error_message

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Для начала работы введите /generate для генерации истории.')
    create_database()

# Обработчик команды /generate
@bot.message_handler(commands=['generate'])
def generate(message):
    bot.reply_to(message, 'Выберите жанр: Фэнтези, Научная фантастика, Боевик, Романтика.')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Обработка текстового сообщения
    text = message.text
    user_id = message.from_user.id

    # Получаем параметры пользователя из базы данных
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            genre, gender, universe = user_data[1], user_data[2], user_data[3]

            # Проверяем, выбраны ли все параметры
            if genre and gender and universe:
                # Генерируем текст с помощью Yandex GPT
                generated_text = generate_text(genre, gender, universe, text)
                bot.reply_to(message, generated_text)
            else:
                bot.reply_to(message, 'Не выбраны все параметры для генерации истории.')
        else:
            bot.reply_to(message, 'Не удалось получить данные пользователя.')

# Запуск бота
bot.polling()