from bot_instance import bot, ADMIN_IDS, CHAT_LINK
from utils.database import load, save
from utils.logger import send_pretty_log
from handlers.keyboards import main_keyboard
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def request_chat_access(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if user_id not in data["users"]:
        bot.send_message(message.chat.id, "❌ Сначала пройди регистрацию.")
        return
    
    user = data["users"][user_id]
    
    # Уже есть доступ
    if user.get("chat_access", False):
        bot.send_message(message.chat.id, f"✅ Ты уже в чате:\n{CHAT_LINK}")
        return
    
    # Запрос уже отправлен
    if user.get("chat_requested", False):
        bot.send_message(message.chat.id, "⏳ Запрос уже отправлен. Ожидай решения.")
        return
    
    # Отправляем запрос админу с инлайн-кнопками
    user["chat_requested"] = True
    save(data)
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    approve_btn = InlineKeyboardButton(
        "✅ Принять",
        callback_data=f"approve_{user['hex']}"
    )
    reject_btn = InlineKeyboardButton(
        "❌ Отклонить",
        callback_data=f"reject_{user['hex']}"
    )
    keyboard.add(approve_btn, reject_btn)
    
    for _admin in ADMIN_IDS:
        try:
            bot.send_message(
                _admin,
                f"🔔 ЗАПРОС ДОСТУПА В ЧАТ\n\n"
                f"Пользователь: {user.get('user_tag', 'Без тега')}\n"
                f"Hex: {user.get('hex')}\n"
                f"ID: {user_id}",
                reply_markup=keyboard
            )
        except Exception:
            continue
    
    bot.send_message(
        message.chat.id,
        "📨 Запрос на доступ в чат отправлен администратору.\n"
        "Ожидай решения.",
        reply_markup=main_keyboard(False)
    )
    
    send_pretty_log("🔔", f"[CHAT REQUEST] {user['hex']} запросил доступ")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve_', 'reject_')))
def handle_chat_decision(call):
    action, target_hex = call.data.split('_', 1)
    data = load()
    
    for uid, user in data["users"].items():
        if user.get("hex") == target_hex:
            if action == "approve":
                user["chat_access"] = True
                user["chat_requested"] = False
                save(data)
                
                bot.send_message(
                    int(uid),
                    f"✅ Доступ в чат одобрен!\n\nСсылка: {CHAT_LINK}",
                    reply_markup=main_keyboard(True)
                )
                
                bot.edit_message_text(
                    f"✅ Доступ одобрен для {target_hex}",
                    call.message.chat.id,
                    call.message.message_id
                )
                
                send_pretty_log("✅", f"[CHAT APPROVED] {target_hex}")
                
            elif action == "reject":
                user["chat_requested"] = False
                save(data)
                
                bot.send_message(
                    int(uid),
                    "❌ Доступ в чат отклонён.\n"
                    "Если хочешь запросить снова — нажми кнопку.",
                    reply_markup=main_keyboard(False)
                )
                
                bot.edit_message_text(
                    f"❌ Доступ отклонён для {target_hex}",
                    call.message.chat.id,
                    call.message.message_id
                )
                
                send_pretty_log("❌", f"[CHAT REJECTED] {target_hex}")
            
            bot.answer_callback_query(call.id)
            return
    
    bot.answer_callback_query(call.id, "❌ Пользователь не найден")