import time
import random
import json
import os
from datetime import datetime

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_time():
    return datetime.now().strftime("%H:%M:%S")

def human_delay(min_s=1.0, max_s=3.0):
    """محاكاة تأخير بشري"""
    time.sleep(random.uniform(min_s, max_s))

def save_results(username, data, output_dir="results"):
    """حفظ النتائج في ملف"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{username}_{int(time.time())}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_config(path="config.json"):
    """تحميل الإعدادات"""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def format_number(n):
    """تنسيق الأرقام"""
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    elif n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)
