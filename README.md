# NovaX - Advanced Multi-Vector Penetration Testing Framework

**Version:** 1.0  
**Platform:** Termux / Linux  
**Language:** Python 3

## 📋 الوصف
إطار عمل متكامل لاختبار الاختراق يجمع بين:
- هجمات رفض الخدمة المتعددة (SYN Flood, HTTP Flood, Slowloris, DNS Amplification)
- هجمات القوة العمياء (SSH, FTP, MySQL, WordPress)
- فحص الثغرات (SQLi, XSS, LFI, RCE)
- تجاوز الحماية (WAF Bypass, CDN Bypass, Rate Limit Bypass)
- الفحص الشامل والمتعدد المراحل

## 🚀 التثبيت على Termux

```bash
pkg update -y && pkg upgrade -y
pkg install -y git python
git clone https://github.com/YOUR_USERNAME/NovaX.git
cd NovaX
bash install.sh
python main.py
