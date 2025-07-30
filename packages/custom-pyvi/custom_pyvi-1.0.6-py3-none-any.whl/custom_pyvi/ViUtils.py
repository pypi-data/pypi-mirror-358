# custom_pyvi/ViUtils.py

import re
import unicodedata

def remove_accents(s: str) -> str:
    """
    Loại bỏ dấu Tiếng Việt khỏi một chuỗi.
    Phiên bản này được tối ưu cho Python 3 và hoàn toàn độc lập.
    """
    s = str(s)
    # Chuẩn hóa Unicode, tách dấu (é -> e + ´)
    s = unicodedata.normalize('NFD', s)
    # Chỉ giữ lại các ký tự không phải là dấu
    s = "".join([c for c in s if not unicodedata.combining(c)])
    # Thay thế đặc biệt cho chữ 'đ'
    s = re.sub(r'đ', 'd', s)
    s = re.sub(r'Đ', 'D', s)
    return s
