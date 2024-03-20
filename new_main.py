import requests
import telebot
from langdetect import detect  # Импортируем функцию для определения языка
from TOKEN import *
import sqlite3

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных SQLite и создание курсора
conn = sqlite3.connect('users.db')
cursor = conn.cursor()


# Функция для отправки запроса к Yandex GPT
def generate_text(query, genre, gender, universe):
    # Определяем URI модели на основе выбранных параметров
    if detect(query) == 'ru':
        model_uri = f"gpt://{FOLDER_ID}/yandexgpt-lite"
    else:
        model_uri = f"gpt://{FOLDER_ID}/yandexgpt-lite-en"

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
                "text": query
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
        return 'Ошибка при обработке запроса.'


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Для начала работы введите /generate для генерации истории.')


# Обработчик команды /generate
@bot.message_handler(commands=['generate'])
def generate(message):
    bot.reply_to(message, 'Выберите жанр и пол главного героя:')


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    # Получение данных пользователя из базы данных
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    # Если данные пользователя не найдены, отправляем сообщение об ошибке
    if not user_data:
        bot.reply_to(message, 'Не удалось получить данные пользователя.')
        return

    bot.reply_to(message, 'Выберите жанр и пол главного героя:')


# Запуск бота
bot.polling()