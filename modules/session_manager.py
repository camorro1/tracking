#!/usr/bin/env python3
"""
مدير الجلسات
- حفظ جلسات Instagram
- استئناف الجلسات
- إدارة cookies و tokens
"""

import json
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.resolve()
SESSIONS_DIR = BASE_DIR / 'sessions'
SESSIONS_DIR.mkdir(exist_ok=True)


class SessionManager:
    """إدارة جلسات Instagram"""

    def __init__(self):
        self.sessions_dir = SESSIONS_DIR

    def save(self, username, session_id, csrf_token=None, cookies=None):
        """حفظ جلسة"""
        session_data = {
            'username': username,
            'session_id': session_id,
            'csrf_token': csrf_token,
            'cookies': cookies or {},
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
        }

        filepath = self.sessions_dir / f"{username}.json"
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

        return filepath

    def load(self, username):
        """تحميل جلسة"""
        filepath = self.sessions_dir / f"{username}.json"
        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            session = json.load(f)

        # تحديث وقت آخر استخدام
        session['last_used'] = datetime.now().isoformat()
        with open(filepath, 'w') as f:
            json.dump(session, f, indent=2)

        return session

    def delete(self, username):
        """حذف جلسة"""
        filepath = self.sessions_dir / f"{username}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_all(self):
        """عرض كل الجلسات"""
        sessions = []
        for f in self.sessions_dir.glob('*.json'):
            with open(f, 'r') as fp:
                data = json.load(fp)
                sessions.append(data)
        return sorted(sessions, key=lambda x: x.get('last_used', ''), reverse=True)
