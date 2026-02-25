from bot_instance import bot
from utils.database import load
from handlers.keyboards import main_keyboard, start_keyboard

def show_profile(message):
    data = load()
    user_id = str(message.from_user.id)
    
    if user_id not in data["users"]:
        bot.send_message(message.chat.id, "[ERROR] Сначала пройди регистрацию.", 
                        reply_markup=start_keyboard())
        return
    
    user = data["users"][user_id]
    invited_count = user.get("invited_stats", {}).get("count", 0)
    leaflet_count = user.get("leaflet_count", 0)
    has_chat = user.get("chat_access", False)
    
    profile = f"┌{'─'*40}┐\n"
    profile += f"│{'ЛИЧНЫЙ КАБИНЕТ':^40}│\n"
    profile += f"├{'─'*40}┤\n"
    profile += f"│ Тег: {user.get('user_tag', 'Без тега'):<32} │\n"
    profile += f"│ Hex: {user.get('hex', 'нет'):<34} │\n"
    profile += f"│ Дата: {user['created']:<33} │\n"
    profile += f"│ Статус: {user['status']:<31} │\n"
    profile += f"│ Приглашено: {invited_count:<27} │\n"
    profile += f"│ Листовок: {leaflet_count:<28} │\n"
    profile += f"│ Чат: {'✅' if has_chat else '❌'}{'':<29} │\n"
    
    if user["inviter"].startswith("0x"):
        profile += f"│ Пригласил: {user['inviter']:<28} │\n"
    else:
        profile += f"│ Пригласил: {'none':<28} │\n"
    
    profile += f"└{'─'*40}┘"
    
    bot.send_message(message.chat.id, f"```{profile}```", parse_mode='Markdown',
                    reply_markup=main_keyboard(has_chat))