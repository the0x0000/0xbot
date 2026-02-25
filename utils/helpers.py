def get_user_tag(user_data):
    username = user_data.get('username')
    first_name = user_data.get('first_name', '')
    last_name = user_data.get('last_name', '')
    if username:
        return f"@{username}"
    elif first_name or last_name:
        name = f"{first_name} {last_name}".strip()
        return name if name else "Без имени"
    else:
        return "Без имени"

def sanitize_answer(text, max_length=50):
    if not text or not isinstance(text, str):
        return ""
    text = ' '.join(text.split())
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    return text

def is_blocked(user_id, data):
    if user_id in data["users"] and data["users"][user_id]["status"] == "inactive":
        return True
    return False