import telebot
import requests
from TOKEN import *
import logging
import os


# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Путь к файлу логов
log_file_path = 'bot.log'

# Убеждаемся, что файл логов существует
if not os.path.exists(log_file_path):
    # Если файл не существует, создаем его
    with open(log_file_path, 'w') as f:
        f.write('')

# Включение логирования
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Включение логирования
logging.basicConfig(filename='bot.log', level=logging.DEBUG)

# Список доступных жанров
genres = ['Хоррор', 'Фантастика', 'Детектив', 'Романтика']

# Список доступных вселенных
universes = ['Средиземье', 'Галактика', 'Земля', 'Мир фэнтези']

# Список доступных персонажей
characters = {
    'Мужской': ['Джон', 'Майк'],
    'Женский': ['Лиза', 'Анна']
}

# Словарь для хранения выбранных пользователем параметров
user_choices = {}

# Функция для отправки запроса к Yandex GPT
def generate_story(user_choices, description):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    query = f"Жанр: {user_choices.get('genre', 'Не указан')}\n" \
            f"Персонажи: {', '.join(user_choices.get('characters', ['Не указано']))}\n" \
            f"Вселенная: {user_choices.get('universe', 'Не указан')}\n" \
            f"Описание: {description}"
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 1,
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
        story = response.json()["result"]["alternatives"][0]["message"]["text"]
        return story
    else:
        logging.error(f'Request failed with status code {response.status_code}')
        return 'Ошибка при обработке запроса.'

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Для начала работы введите /generate для генерации истории.')

# Функция для отправки сообщений о статусах запросов к нейросети
def send_debug_message(chat_id, message):
    bot.send_message(chat_id, f'[DEBUG] {message}')

# Обработчик команды /generate
@bot.message_handler(commands=['generate'])
def generate(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for genre in genres:
        markup.add(telebot.types.KeyboardButton(genre))
    bot.send_message(message.chat.id, 'Выберите жанр:', reply_markup=markup)

# Обработчик текстовых сообщений с выбором жанра
@bot.message_handler(func=lambda message: message.text in genres)
def choose_genre(message):
    genre = message.text
    user_choices['genre'] = genre
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for gender in characters:
        markup.add(telebot.types.KeyboardButton(gender))
    bot.send_message(message.chat.id, 'Выберите пол главного героя:', reply_markup=markup)

# Обработчик текстовых сообщений с выбором пола главного героя
@bot.message_handler(func=lambda message: message.text in characters)
def choose_gender(message):
    gender = message.text
    user_choices['gender'] = gender
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for character in characters[gender]:
        markup.add(telebot.types.KeyboardButton(character))
    bot.send_message(message.chat.id, 'Выберите персонажей:', reply_markup=markup)

# Обработчик текстовых сообщений с выбором персонажей
@bot.message_handler(func=lambda message: message.text in characters.get(user_choices.get('gender', []), set()))
def choose_characters(message):
    character = message.text
    if 'characters' not in user_choices:
        user_choices['characters'] = []
    user_choices['characters'].append(character)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for universe in universes:
        markup.add(telebot.types.KeyboardButton(universe))
    bot.send_message(message.chat.id, 'Выберите вселенную:', reply_markup=markup)

# Обработчик текстовых сообщений с выбором вселенной
@bot.message_handler(func=lambda message: message.text in universes)
def choose_universe(message):
    universe = message.text
    user_choices['universe'] = universe
    bot.send_message(message.chat.id, 'Введите описание для истории:')

# Обработчик текстовых сообщений для генерации истории
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    description = message.text
    # Здесь вызываем функцию для генерации истории на основе выбора пользователя и описания
    generated_story = generate_story(user_choices, description)
    bot.reply_to(message, generated_story)

# Обработчик команды /logs
@bot.message_handler(commands=['logs'])
def send_logs(message):
    try:
        with open('bot.log', 'r') as log_file:
            log_content = log_file.read()
        bot.send_message(message.chat.id, log_content)
    except Exception as e:
        bot.reply_to(message, f'Ошибка отправки логов: {str(e)}')

# Запуск бота
bot.polling()
