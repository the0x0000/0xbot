from bot_instance import bot, ADMIN_LOG_CHAT

def send_pretty_log(emoji, text):
    try:
        bot.send_message(ADMIN_LOG_CHAT, f"{emoji} {text}", parse_mode='Markdown')
    except Exception as e:
        print(f"[LOG ERROR] {e}")