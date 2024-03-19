import telebot
import sqlite3
from TOKEN import *

# Создание соединения с базой данных
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы для хранения данных пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    genre TEXT,
                    gender TEXT,
                    universe TEXT
                )''')
conn.commit()

# Класс для представления состояния пользователя
class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.genre = None
        self.gender = None
        self.universe = None

# Словарь для хранения текущего состояния пользователей
user_states = {}

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем, есть ли пользователь уже в базе данных
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    existing_user = cursor.fetchone()
    if not existing_user:
        # Если пользователя нет, добавляем его в базу данных с пустыми значениями
        cursor.execute('INSERT INTO users VALUES (?, NULL, NULL, NULL)', (message.from_user.id,))
        conn.commit()
        # Создаем объект состояния для нового пользователя
        user_states[message.from_user.id] = UserState(message.from_user.id)
    else:
        # Если пользователь уже есть, загружаем его данные из базы данных
        user_states[message.from_user.id] = UserState(message.from_user.id)
        user_states[message.from_user.id].genre = existing_user[1]
        user_states[message.from_user.id].gender = existing_user[2]
        user_states[message.from_user.id].universe = existing_user[3]

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
    if message.text == 'Фантастика' or message.text == 'Фэнтези' or message.text == 'Детектив' or message.text == 'Романтика':
        user_states[message.from_user.id].genre = message.text
        bot.send_message(message.chat.id, 'Выберите пол главного героя:',
                         reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                        one_time_keyboard=True,
                                                                        keyboard=[
                                                                            ['Мужской', 'Женский']
                                                                        ]))
    elif message.text == 'Мужской' or message.text == 'Женский':
        user_states[message.from_user.id].gender = message.text
        bot.send_message(message.chat.id, 'Выберите вселенную:',
                         reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                        one_time_keyboard=True,
                                                                        keyboard=[
                                                                            ['Земля', 'Другая планета']
                                                                        ]))
    elif message.text == 'Земля' or message.text == 'Другая планета':
        user_states[message.from_user.id].universe = message.text
        # После выбора всех параметров можно вызвать функцию для генерации текста или что-то еще
        bot.send_message(message.chat.id, 'Вы выбрали следующие параметры:\n'
                                          f'Жанр: {user_states[message.from_user.id].genre}\n'
                                          f'Пол главного героя: {user_states[message.from_user.id].gender}\n'
                                          f'Вселенная: {user_states[message.from_user.id].universe}')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйтесь кнопками для выбора.')

# Запуск бота
bot.polling()

# В конце программы закрываем соединение с базой данных
conn.close()