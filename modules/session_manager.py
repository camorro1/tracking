#!/usr/bin/env python3
"""Camoro - Session Manager"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class SessionManager:
    def __init__(self) -> None:
        self.sessions_dir = SESSIONS_DIR

    def save(
        self,
        username: str,
        session_id: str,
        csrf_token: Optional[str] = None,
        cookies: Optional[dict] = None,
    ) -> Path:
        data = {
            "username": username,
            "session_id": session_id,
            "csrf_token": csrf_token or "",
            "cookies": cookies or {},
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
        }
        path = self.sessions_dir / f"{username}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, username: str) -> Optional[Dict[str, Any]]:
        path = self.sessions_dir / f"{username}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        data["last_used"] = datetime.now().isoformat()
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data

    def delete(self, username: str) -> bool:
        path = self.sessions_dir / f"{username}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_all(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for f in self.sessions_dir.glob("*.json"):
            try:
                out.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        return sorted(out, key=lambda x: x.get("last_used", ""), reverse=True)
