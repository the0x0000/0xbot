import json
from datetime import datetime
from bot_instance import DB_FILE


def load():
    try:
        with open(DB_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"users": {}, "last_id": 0}

def save(data):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def new_hex(data):
    data["last_id"] += 1
    return f"0x{data['last_id']:04X}"

def update_invited_stats(data, inviter_hex):
    if inviter_hex == "none" or not inviter_hex.startswith("0x"):
        return
    for user in data["users"].values():
        if user.get("hex") == inviter_hex:
            invited_count = 0
            for u in data["users"].values():
                if u.get("inviter") == inviter_hex:
                    invited_count += 1
            user["invited_stats"] = {
                "count": invited_count,
                "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            break