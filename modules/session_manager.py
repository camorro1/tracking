#!/usr/bin/env python3
"""Camoro - Session Manager"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


class SessionManager:
    def __init__(self):
        self.sessions_dir = SESSIONS_DIR

    def save(self, username, session_id, csrf_token=None, cookies=None):
        data = {
            "username": username,
            "session_id": session_id,
            "csrf_token": csrf_token,
            "cookies": cookies or {},
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
        }
        path = self.sessions_dir / f"{username}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def load(self, username):
        path = self.sessions_dir / f"{username}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["last_used"] = datetime.now().isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data

    def delete(self, username):
        path = self.sessions_dir / f"{username}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_all(self):
        sessions = []
        for f in self.sessions_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    sessions.append(json.load(fp))
            except Exception:
                continue
        return sorted(sessions, key=lambda x: x.get("last_used", ""), reverse=True)
