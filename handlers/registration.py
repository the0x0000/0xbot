from bot_instance import bot, ADMIN_IDS
from time import time
from datetime import datetime
from utils.database import load, save, new_hex, update_invited_stats
from utils.helpers import get_user_tag, sanitize_answer, is_blocked
from utils.logger import send_pretty_log
from handlers.profile import show_profile
from handlers.keyboards import main_keyboard, start_keyboard
from crypto import decrypt_from_url

QUESTIONS = [
    "Как ты сюда попал?",
    "Как тебя зовут? (необязательно)",
    "Сколько тебе лет? (необязательно)",
]
MAX_ANSWER_LENGTH = 50

def start_command(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if is_blocked(user_id, data):
        bot.send_message(message.chat.id, "[ACCESS] Доступ запрещён.")
        return
    
    if user_id in data["users"] and data["users"][user_id].get("hex"):
        show_profile(message)
        return
    
    parts = message.text.split()
    encrypted_ref = parts[1] if len(parts) > 1 else "none"
    real_ref = decrypt_from_url(encrypted_ref)
    
    user_tag = get_user_tag({
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    })
    
    data["users"][user_id] = {
        "telegram_id": message.from_user.id,
        "user_tag": user_tag,
        "hex": None,
        "inviter": real_ref,
        "status": "interview",
        "answers": [],
        "created": datetime.now().strftime("%d.%m.%Y"),
        "invited_stats": {"count": 0, "last_updated": ""},
        "leaflet_count": 0,
        "waiting_for_admin": False,
        "last_admin_msg": None,
        "chat_access": False,
        "chat_requested": False
    }
    save(data)
    
    update_invited_stats(data, real_ref)
    save(data)
    
    send_pretty_log("", f"👤 [NEW] {user_tag} ({user_id}) inviter: {real_ref}")
    
    bot.send_message(message.chat.id,
        f"[START] Регистрация\nПригласитель: {real_ref if real_ref != 'none' else 'отсутствует'}\n\n"
        f"Вопрос 1/{len(QUESTIONS)}:\n{QUESTIONS[0]}\n\n"
        f"*Максимум {MAX_ANSWER_LENGTH} символов*",
        reply_markup=None,
        parse_mode='Markdown')

def start_registration(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if user_id in data["users"] and data["users"][user_id].get("hex"):
        show_profile(message)
        return
    
    user_tag = get_user_tag({
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    })
    
    data["users"][user_id] = {
        "telegram_id": message.from_user.id,
        "user_tag": user_tag,
        "hex": None,
        "inviter": "none",
        "status": "interview",
        "answers": [],
        "created": datetime.now().strftime("%d.%m.%Y"),
        "invited_stats": {"count": 0, "last_updated": ""},
        "leaflet_count": 0,
        "waiting_for_admin": False,
        "last_admin_msg": None,
        "chat_access": False,
        "chat_requested": False
    }
    save(data)
    
    bot.send_message(message.chat.id,
        f"[START] Регистрация\n\n"
        f"Вопрос 1/{len(QUESTIONS)}:\n{QUESTIONS[0]}\n\n"
        f"*Максимум {MAX_ANSWER_LENGTH} символов*",
        reply_markup=None,
        parse_mode='Markdown')

def handle_interview(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if is_blocked(user_id, data):
        bot.send_message(message.chat.id, "[ACCESS] Доступ запрещён.")
        return
    
    if user_id not in data["users"]:
        bot.send_message(message.chat.id,
            "[START] Для регистрации нажми кнопку ниже:",
            reply_markup=start_keyboard())
        return
    
    user = data["users"][user_id]
    user_tag = user.get("user_tag", "Без тега")
    
    if user.get("waiting_for_admin", False):
        user["waiting_for_admin"] = False
        user["last_admin_msg"] = time()
        save(data)
        
        hex_id = user.get("hex", "нет")
        
        for _admin in ADMIN_IDS:
            try:
                bot.send_message(_admin,
                    f"📨 СООБЩЕНИЕ ОТ {user_tag} (hex: {hex_id})\n"
                    f"ID: {user_id}\n\n"
                    f"{message.text}\n\n"
                    f"---\n"
                    f"Ответь на это сообщение, чтобы отправить ответ пользователю.")
            except Exception:
                continue
        
        bot.send_message(message.chat.id,
            "[ADMIN] Сообщение отправлено. Ожидай ответа.",
            reply_markup=main_keyboard())
        return
    
    if user["status"] != "interview":
        bot.send_message(message.chat.id,
            "[MENU] Используй кнопки ниже:",
            reply_markup=main_keyboard())
        return
    
    clean_answer = sanitize_answer(message.text)
    
    if not clean_answer.strip():
        current_question = len(user["answers"])
        bot.send_message(message.chat.id,
            f"[ERROR] Ответ не может быть пустым.\n"
            f"Попробуй ещё раз:\n{QUESTIONS[current_question]}\n\n"
            f"*Максимум {MAX_ANSWER_LENGTH} символов*",
            parse_mode='Markdown')
        return
    
    user["answers"].append(clean_answer)
    
    if len(user["answers"]) < len(QUESTIONS):
        save(data)
        current_question = len(user["answers"])
        bot.send_message(message.chat.id,
            f"[OK] Ответ сохранен.\n\n"
            f"Вопрос {current_question + 1}/{len(QUESTIONS)}:\n{QUESTIONS[current_question]}\n\n"
            f"*Максимум {MAX_ANSWER_LENGTH} символов*",
            parse_mode='Markdown')
    else:
        hex_id = new_hex(data)
        user["hex"] = hex_id
        user["status"] = "active"
        user["invited_stats"] = {"count": 0, "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M")}
        user["leaflet_count"] = 0
        save(data)
        
        if user["inviter"] != "none" and user["inviter"].startswith("0x"):
            for uid, u in data["users"].items():
                if u.get("hex") == user["inviter"] and u.get("status") == "active":
                    try:
                        bot.send_message(
                            u["telegram_id"],
                            f"🎉 Новый участник по вашей листовке!\n\n"
                            f"Hex новичка: {hex_id}\n"
                            f"Тег: {user_tag}\n\n"
                            f"Спасибо, что развиваете OMEN.",
                            parse_mode=None
                        )
                        send_pretty_log("🔗", f"[INVITE] {user['inviter']} → {hex_id}")
                    except Exception as e:
                        print(f"Не удалось уведомить инвайтера {user['inviter']}: {e}")
                    break
        
        update_invited_stats(data, user["inviter"])
        save(data)
        
        log_data = (
            f"🆕 [NEW PLAYER] {hex_id} ({user_tag})\n"
            f"   Пригласил: {user['inviter']}\n"
            f'   Ответы: "{user["answers"][0]}", "{user["answers"][1]}", "{user["answers"][2]}"'
        )
        send_pretty_log("", log_data)
        
        box = f"┌{'─'*40}┐\n"
        box += f"│{'РЕГИСТРАЦИЯ ЗАВЕРШЕНА'}\n"
        box += f"├{'─'*40}┤\n"
        box += f"│ Hex ID: {hex_id}\n"
        box += f"├{'─'*40}┤\n"
        box += f"│{'Ответы:'}\n"
        
        for i, answer in enumerate(user["answers"], 1):
            if len(answer) > 35:
                answer_display = answer[:32] + "..."
            else:
                answer_display = answer
            box += f"│ {i}. {answer_display}\n"
        
        box += f"├{'─'*40}┤\n"
        box += f"│ Используй кнопки ниже          \n"
        box += f"└{'─'*40}┘"
        
        bot.send_message(message.chat.id, f"```{box}```", parse_mode='Markdown',
                        reply_markup=main_keyboard())

def handle_buttons(message):
    if message.text == "[ Начать регистрацию ]":
        start_registration(message)
    elif message.text == "[ Личный кабинет ]":
        show_profile(message)