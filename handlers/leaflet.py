from bot_instance import bot
import os
import tempfile
from utils.database import load, save
from utils.spam_protection import check_spam
from utils.logger import send_pretty_log
from handlers.keyboards import main_keyboard, start_keyboard
from crypto import encrypt_for_url
from leaflet_generator import create_leaflet_html

def create_leaflet_handler(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if user_id not in data["users"] or not data["users"][user_id].get("hex"):
        bot.send_message(message.chat.id, "[ERROR] Сначала пройди регистрацию.",
                        reply_markup=start_keyboard())
        return
    
    can_proceed, spam_message = check_spam(user_id)
    if not can_proceed:
        bot.send_message(message.chat.id, spam_message, reply_markup=main_keyboard())
        return
    
    hex_id = data["users"][user_id]["hex"]
    user_tag = data["users"][user_id].get("user_tag", "Без тега")
    
    data["users"][user_id]["leaflet_count"] = data["users"][user_id].get("leaflet_count", 0) + 1
    leaflet_count = data["users"][user_id]["leaflet_count"]
    save(data)
    
    try:
        html_path = create_leaflet_html(hex_id, encrypt_for_url)
        
        with open(html_path, 'rb') as html_file:
            bot.send_document(
                message.chat.id,
                html_file,
                visible_file_name=f"OMEN_leaflet_{hex_id}.html",
                caption=f"[OK] Листовка для {hex_id}\n\n"
                        f"*Открой в браузере и нажми кнопку 'Скачать PNG'*",
                parse_mode='Markdown',
                reply_markup=main_keyboard()
            )
        
        os.remove(html_path)
        send_pretty_log("📄", f"[LEAFLET] {hex_id} создал листовку (всего: {leaflet_count})")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"[ERROR] {e}", reply_markup=main_keyboard())
        send_pretty_log("⚠️", f"[ERROR] Ошибка генерации листовки у {hex_id}: {str(e)[:100]}")