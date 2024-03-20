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
    user_id = message.from_user.id
    conn = sqlite3.connect('users.db')  # Подключение к базе данных
    cursor = conn.cursor()
    user_data = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()

    if user_data:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Фантастика', 'Фэнтези')
        markup.add('Мужской', 'Женский')
        markup.add('Вселенная 1', 'Вселенная 2')
        bot.reply_to(message, 'Выберите жанр и пол главного героя:', reply_markup=markup)
    else:
        bot.reply_to(message, 'Не удалось получить данные пользователя.')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
	user_id = message.from_user.id

	# Подключаемся к базе данных и создаем курсор внутри этого потока
	with sqlite3.connect('users.db') as conn:
		cursor = conn.cursor()
		user_data = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
		if not user_data:
			bot.reply_to(message, 'Не удалось получить данные пользователя.')
			return

	query = message.text
	generated_text = generate_text(query, user_data[4], user_data[5], user_data[6])
	bot.reply_to(message, generated_text)


# Запуск бота
bot.polling()
