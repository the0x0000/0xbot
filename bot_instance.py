import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
_admin_ids_env = os.getenv("ADMIN_IDS")
if _admin_ids_env:
	ADMIN_IDS = [int(x.strip()) for x in _admin_ids_env.split(',') if x.strip()]
else:
	# fallback to single ADMIN_ID for compatibility
	_single_admin = os.getenv("ADMIN_ID")
	ADMIN_IDS = [int(_single_admin)] if _single_admin else []

# For convenience keep ADMIN_ID as the first admin or None
ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else None
ADMIN_LOG_CHAT = int(os.getenv("ADMIN_LOG_CHAT")) if os.getenv("ADMIN_LOG_CHAT") else None
ADMIN_IDS_SET = set(ADMIN_IDS)
CHAT_LINK = os.getenv("CHAT_LINK")
DB_FILE = os.getenv("DB_FILE", "users.json")
#1
bot = telebot.TeleBot(BOT_TOKEN)