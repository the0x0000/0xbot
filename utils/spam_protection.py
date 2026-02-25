from time import time
from threading import Lock
from datetime import datetime

user_cooldowns = {}
cooldown_lock = Lock()
COOLDOWN_SECONDS = 10
MAX_GENERATIONS_PER_DAY = 30
user_daily_counts = {}
last_reset_day = datetime.now().day

def check_spam(user_id):
    global last_reset_day, user_daily_counts
    with cooldown_lock:
        current_day = datetime.now().day
        if current_day != last_reset_day:
            user_daily_counts.clear()
            last_reset_day = current_day
        if user_id in user_cooldowns:
            last_gen = user_cooldowns[user_id]
            if time() - last_gen < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - (time() - last_gen))
                return False, f"[WAIT] {remaining} сек"
        if user_id in user_daily_counts:
            if user_daily_counts[user_id] >= MAX_GENERATIONS_PER_DAY:
                return False, "[LIMIT] 30 в день"
        user_cooldowns[user_id] = time()
        user_daily_counts[user_id] = user_daily_counts.get(user_id, 0) + 1
        remaining = MAX_GENERATIONS_PER_DAY - user_daily_counts[user_id]
        return True, f"[OK] Осталось: {remaining}"