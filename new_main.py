import telebot
import sqlite3
from TOKEN import *

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Создание соединения с базой данных
conn = sqlite3.connect('user_data.db')

# Создание объекта курсора
cursor = conn.cursor()

# Создание таблицы пользователей, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  user_id INTEGER PRIMARY KEY,
                  genre TEXT,
                  gender TEXT,
                  universe TEXT
                )''')

# Коммит изменений и закрытие соединения
conn.commit()
conn.close()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Подключение к базе данных
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Проверка, есть ли пользователь в базе данных
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    existing_user = cursor.fetchone()

    # Если пользователя нет, добавляем его в базу данных с пустыми значениями
    if not existing_user:
        cursor.execute('INSERT INTO users (user_id, genre, gender, universe) VALUES (?, NULL, NULL, NULL)', (message.from_user.id,))
        conn.commit()

    # Закрываем соединение с базой данных
    conn.close()

    # Отправляем приветственное сообщение и кнопки для выбора жанра, пола героя и вселенной
    bot.send_message(message.chat.id, 'Привет! Для начала работы выберите жанр:',
                     reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                    one_time_keyboard=True,
                                                                    keyboard=[
                                                                        ['Фантастика', 'Фэнтези'],
                                                                        ['Детектив', 'Романтика']
                                                                    ]))

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Подключение к базе данных
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Обработка текстового сообщения
    genre = message.text
    user_id = message.from_user.id

    # Обновляем жанр пользователя в базе данных
    cursor.execute('UPDATE users SET genre = ? WHERE user_id = ?', (genre, user_id))
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()

    # Отправляем сообщение с предложением выбрать пол главного героя
    bot.send_message(message.chat.id, 'Отлично! Теперь выберите пол главного героя:',
                     reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                    one_time_keyboard=True,
                                                                    keyboard=[
                                                                        ['Мужской', 'Женский']
                                                                    ]))

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Подключение к базе данных
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Обработка текстового сообщения
    gender = message.text
    user_id = message.from_user.id

    # Обновляем пол главного героя в базе данных
    cursor.execute('UPDATE users SET gender = ? WHERE user_id = ?', (gender, user_id))
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()

    # Отправляем сообщение с предложением выбрать вселенную
    bot.send_message(message.chat.id, 'Отлично! Теперь выберите вселенную:',
                     reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                    one_time_keyboard=True,
                                                                    keyboard=[
                                                                        ['Вселенная 1', 'Вселенная 2']
                                                                    ]))

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Подключение к базе данных
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Обработка текстового сообщения
    universe = message.text
    user_id = message.from_user.id

    # Обновляем вселенную в базе данных
    cursor.execute('UPDATE users SET universe = ? WHERE user_id = ?', (universe, user_id))
    conn.commit()

    # Закрываем соединение с базой данных
    conn.close()

    # Отправляем сообщение с подтверждением выбора
    bot.send_message(message.chat.id, 'Отлично! Ваши предпочтения сохранены.')

# Запуск бота
bot.polling()