import random
import string
import base64

SECRET_KEY = "roæθg"
USE_SIMPLE = True

def is_hex_like(text):
    return text.startswith("0x") and len(text) > 2

def encrypt_simple(hex_code):
    if hex_code == "none":
        return "none"
    
    if not is_hex_like(hex_code):
        return hex_code
    
    data = hex_code[2:]
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    to_encode = f"{data}|{salt}"
    encoded = base64.urlsafe_b64encode(to_encode.encode()).decode().rstrip("=")
    return encoded

def decrypt_simple(encrypted):
    if encrypted == "none":
        return "none"
    
    if encrypted.startswith("0x"):
        return encrypted
    
    try:
        padding = 4 - (len(encrypted) % 4)
        if padding != 4:
            encrypted += "=" * padding
        
        decoded = base64.urlsafe_b64decode(encrypted).decode()
        
        if "|" not in decoded:
            return encrypted
        
        data, salt = decoded.split("|", 1)
        return f"0x{data}"
    
    except Exception as e:
        print(f"Decrypt error: {e}")
        return encrypted

def encrypt_for_url(hex_code):
    if hex_code == "none" or not hex_code.startswith("0x"):
        return hex_code
    
    if USE_SIMPLE:
        return encrypt_simple(hex_code)
    else:
        return hex_code

def decrypt_from_url(encrypted):
    if encrypted == "none":
        return "none"
    
    if USE_SIMPLE:
        return decrypt_simple(encrypted)
    else:
        return encrypted