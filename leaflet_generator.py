import os
import tempfile
import qrcode
import qrcode.constants
import base64
from PIL import Image
from datetime import datetime

def create_leaflet_html(hex_id, encrypt_func):
    encrypted = encrypt_func(hex_id)
    url = f"https://halareka.github.io/0?ref={encrypted}"
    
    qr = qrcode.QRCode(
        version=5,
        box_size=5,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((400, 400), Image.Resampling.LANCZOS)
    
    qr_path = os.path.join(tempfile.gettempdir(), f"qr_{hex_id}_{int(datetime.now().timestamp())}.png")
    qr_img.save(qr_path, dpi=(300, 300))
    
    with open('leaflet_template.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    hex_formatted = hex_id.replace('0x', '0<span style="position: relative; top: -2px;">x</span>')
    html_content = html_content.replace(
        '0<span style="position: relative; top: -2px;">x</span>0000', 
        hex_formatted
    )
    
    with open('Group 38.svg', 'rb') as f:
        svg1 = base64.b64encode(f.read()).decode()
    html_content = html_content.replace('Group 38.svg', f'data:image/svg+xml;base64,{svg1}')
    
    with open('Group 39.svg', 'rb') as f:
        svg2 = base64.b64encode(f.read()).decode()
    html_content = html_content.replace('Group 39.svg', f'data:image/svg+xml;base64,{svg2}')
    
    with open(qr_path, 'rb') as f:
        qr_base64 = base64.b64encode(f.read()).decode()
    html_content = html_content.replace('image 1.png', f'data:image/png;base64,{qr_base64}')
    
    html_filename = f"leaflet_{hex_id}_{int(datetime.now().timestamp())}.html"
    html_path = os.path.join(tempfile.gettempdir(), html_filename)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    os.remove(qr_path)
    return html_path