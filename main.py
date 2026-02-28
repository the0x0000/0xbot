from bot_instance import bot, ADMIN_ID
import atexit
import time
from utils.logger import send_pretty_log
from handlers.registration import handle_interview, start_command, handle_buttons
from handlers.admin import admin_send_command, handle_admin_reply, contact_admin_handler
from handlers.leaflet import create_leaflet_handler
from handlers.profile import show_profile
from handlers.keyboards import main_keyboard, start_keyboard
from handlers.admin_commands import (
    users_list, user_info, stats, top_inviters, set_status, backup_db
)
from handlers.chat_access import request_chat_access, handle_chat_decision

#КОМАНДЫ .
@bot.message_handler(commands=['start', 'cancel'])
def start_cmd(message):
    start_command(message)

@bot.message_handler(commands=['send'])
def send_cmd(message):
    admin_send_command(message)

@bot.message_handler(commands=['users'])
def users_cmd(message):
    users_list(message)

@bot.message_handler(commands=['user'])
def user_cmd(message):
    user_info(message)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    stats(message)

@bot.message_handler(commands=['top'])
def top_cmd(message):
    top_inviters(message)

@bot.message_handler(commands=['setstatus'])
def setstatus_cmd(message):
    set_status(message)

@bot.message_handler(commands=['backup'])
def backup_cmd(message):
    backup_db(message)

@bot.message_handler(commands=['approve'])
def approve_cmd(message):

    bot.reply_to(message, "❌ Используй инлайн-кнопки в уведомлении")

@bot.message_handler(commands=['reject'])
def reject_cmd(message):
    bot.reply_to(message, "❌ Используй инлайн-кнопки в уведомлении")

#КНОПКИ
@bot.message_handler(func=lambda m: m.text in [
    "[ Начать регистрацию ]",
    "[ Личный кабинет ]",
    "[ Сгенерировать листовку ]",
    "[ Запросить доступ в чат ]",
    "[ 📨 Связь с админом ]"
])
def buttons_handler(message):
    if message.text == "[ Личный кабинет ]":
        show_profile(message)
    elif message.text == "[ Сгенерировать листовку ]":
        create_leaflet_handler(message)
    elif message.text == "[ Запросить доступ в чат ]":
        request_chat_access(message)
    elif message.text == "[ 📨 Связь с админом ]":
        contact_admin_handler(message)
    elif message.text == "[ Начать регистрацию ]":
        from handlers.registration import start_registration
        start_registration(message)

#ОТВЕТЫ АДМИНА
@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id == ADMIN_ID)
def admin_reply_handler(message):
    handle_admin_reply(message)

#ВСЁ ОСТАЛЬНОЕ
@bot.message_handler(func=lambda m: True)
def all_messages_handler(message):
    handle_interview(message)

#АПУСК
if __name__ == "__main__":
    print("[OK] Bot запускается...")
    atexit.register(lambda: send_pretty_log("⛔", "[STOP] Бот остановлен"))
    send_pretty_log("🚀", "[START] Бот запущен")
    
    while True:
        try:
            print("[OK] Запуск polling...")
            bot.polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            error_text = str(e)
            print(f"[ERROR] {error_text}")
            send_pretty_log("⚠️", f"[RESTART] Бот упал: {error_text[:200]}. Перезапуск через 5 сек...")
            time.sleep(5)
            continue
        break