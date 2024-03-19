from TOKEN import *
import telebot
import sqlite3

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Создание соединения с базой данных
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы пользователей, если ее еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  user_id INTEGER PRIMARY KEY,
                  genre TEXT,
                  gender TEXT,
                  universe TEXT
                )''')

# Коммит изменений
conn.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Отправляем приветственное сообщение и кнопки для выбора жанра
    bot.send_message(message.chat.id, 'Привет! Для начала работы выберите жанр:',
                     reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                    one_time_keyboard=True)
                                    .add('Фантастика', 'Фэнтези')
                                    .add('Детектив', 'Романтика'))

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Обработка текстового сообщения
    text = message.text
    user_id = message.from_user.id

    # Получаем текущий шаг пользователя из базы данных
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        # Обновляем данные пользователя в базе данных в зависимости от текущего шага
        genre, gender, universe = user_data

        if not genre:
            cursor.execute('UPDATE users SET genre = ? WHERE user_id = ?', (text, user_id))
            conn.commit()
            bot.send_message(message.chat.id, 'Отлично! Теперь выберите пол главного героя:',
                             reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                            one_time_keyboard=True)
                                            .add('Мужской', 'Женский'))
        elif not gender:
            cursor.execute('UPDATE users SET gender = ? WHERE user_id = ?', (text, user_id))
            conn.commit()
            bot.send_message(message.chat.id, 'Отлично! Теперь выберите вселенную:',
                             reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                            one_time_keyboard=True)
                                            .add('Вселенная 1', 'Вселенная 2'))
        elif not universe:
            cursor.execute('UPDATE users SET universe = ? WHERE user_id = ?', (text, user_id))
            conn.commit()
            bot.send_message(message.chat.id, 'Отлично! Ваши предпочтения сохранены.')
        else:
            bot.send_message(message.chat.id, 'Вы уже выбрали все параметры.')

    else:
        # В базе данных еще нет записи о пользователе, создаем новую
        cursor.execute('INSERT INTO users (user_id, genre) VALUES (?, ?)', (user_id, text))
        conn.commit()
        bot.send_message(message.chat.id, 'Отлично! Теперь выберите пол главного героя:',
                         reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                                        one_time_keyboard=True)
                                        .add('Мужской', 'Женский'))

# Запуск бота
bot.polling()