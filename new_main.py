import threading
import requests
import telebot
from langdetect import detect
from TOKEN import *
import sqlite3

bot = telebot.TeleBot(TOKEN)
lock = threading.Lock()

def generate_text(query, genre, gender, universe):
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

def get_user_data(user_id):
    with lock:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        user_data = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        conn.close()
    return user_data

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Чтобы начать, введите /generate для генерации истории.')

@bot.message_handler(commands=['generate'])
def generate(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    genre_btn = telebot.types.KeyboardButton('Жанр')
    gender_btn = telebot.types.KeyboardButton('Пол')
    universe_btn = telebot.types.KeyboardButton('Вселенная')
    keyboard.add(genre_btn, gender_btn, universe_btn)
    bot.send_message(message.chat.id, 'Выберите жанр, пол и вселенную:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if not user_data:
        bot.reply_to(message, 'Не удалось получить данные пользователя.')
        return

    if message.text == 'Жанр':
        genre_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        # Добавьте варианты жанров здесь
        bot.send_message(message.chat.id, 'Выберите жанр:', reply_markup=genre_keyboard)
    elif message.text == 'Пол':
        gender_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        # Добавьте варианты полов здесь
        bot.send_message(message.chat.id, 'Выберите пол:', reply_markup=gender_keyboard)
    elif message.text == 'Вселенная':
        universe_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        # Добавьте варианты вселенных здесь
        bot.send_message(message.chat.id, 'Выберите вселенную:', reply_markup=universe_keyboard)
    else:
        query = message.text
        generated_text = generate_text(query, user_data[4], user_data[5], user_data[6])
        bot.reply_to(message, generated_text)

bot.polling()