import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_LOG_CHAT = int(os.getenv("ADMIN_LOG_CHAT"))
CHAT_LINK = os.getenv("CHAT_LINK")
DB_FILE = os.getenv("DB_FILE", "users.json")

bot = telebot.TeleBot(BOT_TOKEN)