import telebot
import datetime
import time
import threading

# Укажите токен вашего бота
API_TOKEN = '7764802749:AAH31695UtnjP9qykA1eayjSAKgl6Tmtr6o'

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения состояний пользователей
user_states = {}

# Статусы для пользователей
WAITING_FOR_TEXT = 1
WAITING_FOR_DATE = 2

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     ("👋🏻Привет! Я бот компании VitaminEnergy.\n\n"
                      "Могу напоминать тебе, когда нужно принимать витамины, введи команду /remind"))


# Обработчик команды /remind
@bot.message_handler(commands=['remind'])
def remind(message):
    # Переводим пользователя в состояние ожидания текста уведомления
    user_states[message.chat.id] = {'state': WAITING_FOR_TEXT}
    bot.send_message(message.chat.id, "Пожалуйста, введите текст уведомления:")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_user_input(message):
    user_data = user_states.get(message.chat.id)

    # Получаем текущее время для примеров
    now = datetime.datetime.now()
    examples = f"""
Примеры:
{(now + datetime.timedelta(minutes=10)).strftime('%d.%m.%Y %H:%M')} - через 10 минут
{(now + datetime.timedelta(hours=1)).strftime('%d.%m.%Y %H:%M')} - через час
{(now + datetime.timedelta(days=1)).strftime('%d.%m.%Y %H:%M')} - через день
{(now + datetime.timedelta(weeks=1)).strftime('%d.%m.%Y %H:%M')} - через неделю
"""

    # Если бот ждет текст уведомления
    if user_data['state'] == WAITING_FOR_TEXT:
        user_data['text'] = message.text  # Сохраняем текст уведомления
        user_data['state'] = WAITING_FOR_DATE  # Переходим в состояние ожидания даты
        bot.send_message(message.chat.id, f"Теперь укажите дату и время в формате дд.мм.гггг чч:мм.\n\n{examples}")

    # Если бот ждет дату
    elif user_data['state'] == WAITING_FOR_DATE:
        try:
            # Парсим введённую дату
            reminder_time = datetime.datetime.strptime(message.text, '%d.%m.%Y %H:%M')

            # Проверяем, не является ли время прошедшим
            if reminder_time <= now:
                bot.send_message(message.chat.id, f"Указанное время уже прошло!\nСегодняшняя дата: {now.strftime('%d.%m.%Y %H:%M')}.")
                return

            # Установка напоминания
            set_reminder(message.chat.id, reminder_time, user_data['text'])

            # Сообщаем пользователю об успешной установке напоминания
            bot.send_message(message.chat.id, f"Напоминание установлено на {reminder_time.strftime('%d.%m.%Y %H:%M')}")
            bot.send_message(message.chat.id, f"Текст напоминания: {user_data['text']} ")

            # Удаляем данные о пользователе после установки напоминания
            user_states.pop(message.chat.id)

        except ValueError:
            bot.send_message(message.chat.id,
                             f"Неправильный формат даты! Попробуйте снова ввести дату и время в формате дд.мм.гггг чч:мм.\n\n{examples}")



# Функция для установки напоминания
def set_reminder(chat_id, target_time, reminder_message):
    # Запускаем в отдельном потоке, чтобы не блокировать основную работу бота
    def reminder_thread():
        # Рассчитываем задержку
        delay = (target_time - datetime.datetime.now()).total_seconds()
        if delay > 0:
            time.sleep(delay)  # Ждем до нужного времени
            bot.send_message(chat_id, f"❗️❗️❗Напоминание❗️❗️️❗️\n\n{reminder_message}")

    # Запускаем напоминание в отдельном потоке
    threading.Thread(target=reminder_thread).start()


# Запуск бота
bot.polling(none_stop=True)
