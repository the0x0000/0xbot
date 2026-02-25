from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(user_has_chat=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("[ Личный кабинет ]"))
    keyboard.add(KeyboardButton("[ Сгенерировать листовку ]"))
    
    if not user_has_chat:
        keyboard.add(KeyboardButton("[ Запросить доступ в чат ]"))
    
    keyboard.add(KeyboardButton("[ 📨 Связь с админом ]"))
    return keyboard

def start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("[ Начать регистрацию ]"))
    return keyboard