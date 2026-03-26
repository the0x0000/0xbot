from bot_instance import bot, ADMIN_IDS
from utils.database import load, save
from utils.logger import send_pretty_log
from handlers.keyboards import main_keyboard, start_keyboard
from time import time

ADMIN_COOLDOWN = 600


def contact_admin_handler(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if user_id not in data["users"]:
        bot.send_message(message.chat.id, "[ERROR] Сначала пройди регистрацию.",
                        reply_markup=start_keyboard())
        return
    
    user = data["users"][user_id]
    
    if user.get("waiting_for_admin", False):
        bot.send_message(message.chat.id,
            "⏳ Ты уже отправил сообщение. Жди ответа администратора.",
            reply_markup=main_keyboard())
        return
    
    last_msg = user.get("last_admin_msg")
    if last_msg:
        time_passed = time() - last_msg
        if time_passed < ADMIN_COOLDOWN:
            remaining = int(ADMIN_COOLDOWN - time_passed)
            minutes = remaining // 60
            seconds = remaining % 60
            bot.send_message(message.chat.id,
                f"⏳ Можно отправить сообщение раз в 10 минут.\n"
                f"Подожди ещё {minutes} мин {seconds} сек.",
                reply_markup=main_keyboard())
            return
    
    user["waiting_for_admin"] = True
    save(data)
    
    bot.send_message(message.chat.id,
        "[ADMIN] Напиши сообщение для администратора.\n"
        "Он ответит как только сможет.\n\n"
        "Отмена — /cancel",
        reply_markup=None)

def admin_send_command(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Использование: /send <hex или @username>")
        return
    
    target = parts[1].strip()
    data = load()
    
    target_id = None
    target_hex = None
    target_tag = None
    
    if target.startswith('0x'):
        for uid, u in data["users"].items():
            if u.get("hex") == target:
                target_id = u["telegram_id"]
                target_hex = target
                target_tag = u.get("user_tag", "Без тега")
                break
    elif target.startswith('@'):
        for uid, u in data["users"].items():
            if u.get("user_tag", "").lower() == target.lower():
                target_id = u["telegram_id"]
                target_hex = u.get("hex", "?")
                target_tag = target
                break
    
    if not target_id:
        bot.reply_to(message, "❌ Пользователь не найден.")
        return
    
    bot.reply_to(message, f"✏️ Введи сообщение для {target_tag} ({target_hex}):")
    bot.register_next_step_handler(message, lambda m: send_to_user(m, target_id, target_tag, target_hex))

def send_to_user(message, target_id, target_tag, target_hex):
    if not message.text:
        bot.reply_to(message, "❌ Пустое сообщение. Отмена.")
        return
    
    try:
        bot.send_message(target_id,
            f"📨 Сообщение от администратора:\n\n{message.text}")
        bot.reply_to(message, f"✅ Сообщение отправлено {target_tag} ({target_hex})")
        send_pretty_log("📨", f"[ADMIN] → {target_hex}: {message.text[:50]}...")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

def handle_admin_reply(message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return
    
    if "ID:" in message.reply_to_message.text:
        lines = message.reply_to_message.text.split('\n')
        for line in lines:
            if line.startswith("ID:"):
                user_id = line.replace("ID:", "").strip()
                
                bot.send_message(user_id,
                    f"[ADMIN] Ответ от администратора:\n\n{message.text}",
                    reply_markup=main_keyboard())
                
                bot.reply_to(message, "[OK] Ответ отправлен пользователю.")
                return