from bot_instance import bot, ADMIN_IDS
from utils.database import load, save
from utils.logger import send_pretty_log
from datetime import datetime
import os
import shutil

def admin_required(func):
    def wrapper(message):
        if message.from_user.id not in ADMIN_IDS:
            bot.reply_to(message, "⛔ Доступ запрещён.")
            return
        return func(message)
    return wrapper


@admin_required
def users_list(message):
    data = load()
    total = len(data["users"])
    active = sum(1 for u in data["users"].values() if u.get("status") == "active")
    inactive = sum(1 for u in data["users"].values() if u.get("status") == "inactive")
    interview = sum(1 for u in data["users"].values() if u.get("status") == "interview")
    
    text = f"👥 Всего: {total}\n✅ Активных: {active}\n❌ Неактивных: {inactive}\n🔄 В процессе: {interview}\n\n"
    
    for uid, user in list(data["users"].items())[:20]:
        hex_id = user.get("hex", "нет")
        tag = user.get("user_tag", "Без тега")
        status = user.get("status", "?")
        text += f"`{hex_id}` – {tag} ({status})\n"
    
    if len(data["users"]) > 20:
        text += f"\n... и ещё {len(data['users']) - 20}"
    
    bot.send_message(message.chat.id, text, parse_mode='none')

@admin_required
def user_info(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Использование: /user <hex>")
        return
    
    target_hex = parts[1].strip()
    data = load()
    
    for uid, user in data["users"].items():
        if user.get("hex") == target_hex:
            invited = user.get("invited_stats", {}).get("count", 0)
            leaflet = user.get("leaflet_count", 0)
            answers = "\n   ".join(user.get("answers", ["—"]))
            
            text = (
                f"👤 Информация о {target_hex}\n\n"
                f"📱 Тег: {user.get('user_tag', '—')}\n"
                f"🆔 Telegram ID: {uid}\n"
                f"📅 Дата: {user.get('created', '—')}\n"
                f"⚡ Статус: {user.get('status', '—')}\n"
                f"📎 Пригласил: {user.get('inviter', 'none')}\n"
                f"👥 Приглашено: {invited}\n"
                f"📄 Листовок: {leaflet}\n"
                f"💬 Ответы:\n   {answers}"
            )
            
            bot.send_message(message.chat.id, text)
            return
    
    bot.reply_to(message, "❌ Пользователь не найден.")

@admin_required
def stats(message):
    data = load()
    
    total = len(data["users"])
    active = sum(1 for u in data["users"].values() if u.get("status") == "active")
    inactive = sum(1 for u in data["users"].values() if u.get("status") == "inactive")
    interview = sum(1 for u in data["users"].values() if u.get("status") == "interview")
    
    total_leaflets = sum(u.get("leaflet_count", 0) for u in data["users"].values())
    total_invites = sum(u.get("invited_stats", {}).get("count", 0) for u in data["users"].values())
    
    text = (
        f"📊 **СТАТИСТИКА OMEN**\n\n"
        f"👥 Всего пользователей: {total}\n"
        f"✅ Активных: {active}\n"
        f"❌ Неактивных: {inactive}\n"
        f"🔄 В процессе: {interview}\n\n"
        f"📄 Всего листовок: {total_leaflets}\n"
        f"🔗 Всего приглашений: {total_invites}"
    )
    
    bot.send_message(message.chat.id, text, parse_mode='none')

@admin_required
def top_inviters(message):
    data = load()
    leaders = []
    
    for user in data["users"].values():
        if user.get("hex") and user.get("status") == "active":
            count = user.get("invited_stats", {}).get("count", 0)
            if count > 0:
                leaders.append({
                    "hex": user["hex"],
                    "tag": user.get("user_tag", "Без тега"),
                    "count": count
                })
    
    leaders.sort(key=lambda x: x["count"], reverse=True)
    
    if not leaders:
        bot.send_message(message.chat.id, "🏆 Пока никто никого не пригласил.")
        return
    
    text = "🏆 **ТОП ПРИГЛАШАЮЩИХ**\n\n"
    for i, leader in enumerate(leaders[:10], 1):
        text += f"{i}. `{leader['hex']}` – {leader['tag']} ({leader['count']})\n"
    
    bot.send_message(message.chat.id, text, parse_mode='none')

@admin_required
def set_status(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Использование: /setstatus <hex> <active/inactive/interview>")
        return
    
    target_hex, new_status = parts[1], parts[2]
    
    if new_status not in ["active", "inactive", "interview"]:
        bot.reply_to(message, "❌ Статус должен быть: active / inactive / interview")
        return
    
    data = load()
    found = False
    
    for uid, user in data["users"].items():
        if user.get("hex") == target_hex:
            user["status"] = new_status
            save(data)
            send_pretty_log("⚙️", f"[STATUS] {target_hex} → {new_status}")
            bot.reply_to(message, f"✅ Статус {target_hex} изменён на {new_status}")
            found = True
            break
    
    if not found:
        bot.reply_to(message, "❌ Пользователь не найден.")

@admin_required
def backup_db(message):
    try:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"users_backup_{timestamp}.json")
        
        shutil.copy2("users.json", backup_file)
        
        with open(backup_file, 'rb') as f:
            bot.send_document(
                message.chat.id,
                f,
                visible_file_name=f"users_backup_{timestamp}.json",
                caption=f"✅ Бэкап создан: {timestamp}"
            )
        
        send_pretty_log("💾", f"[BACKUP] Создан бэкап {timestamp}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка создания бэкапа: {e}")