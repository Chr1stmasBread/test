from TOKEN import *
import telebot
import sqlite3

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Функция для установки соединения с базой данных
def get_connection():
    conn = sqlite3.connect('user_data.db', check_same_thread=False)
    return conn

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
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            # Разбираем полученные данные о пользователе
            genre = user_data[1] if len(user_data) >= 2 else None
            gender = user_data[2] if len(user_data) >= 3 else None
            universe = user_data[3] if len(user_data) >= 4 else None

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