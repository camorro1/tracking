#!/usr/bin/env python3
"""Camoro - Information Gathering"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    print("[!] pip install httpx")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

G = "\033[0;32m"
R = "\033[0;31m"
C = "\033[0;36m"
Y = "\033[1;33m"
W = "\033[1;37m"
P = "\033[0;35m"
N = "\033[0m"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Instagram 330.0.0.18.85 Android (34/14; 480dpi; 1080x2400; samsung; SM-S928B; en_US)",
]


class InfoGatherer:
    def __init__(self, username: str, proxy_manager=None) -> None:
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.info: Dict[str, Any] = {
            "username": self.username,
            "exists": None,
            "full_name": None,
            "biography": None,
            "biography_links": [],
            "profile_pic": None,
            "posts_count": 0,
            "followers_count": 0,
            "following_count": 0,
            "is_private": False,
            "is_verified": False,
            "is_business": False,
            "business_category": None,
            "external_url": None,
            "instagram_id": None,
            "source": None,
            "collected_at": datetime.now().isoformat(),
        }

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
        }

    def _client(self) -> httpx.Client:
        kwargs: Dict[str, Any] = {
            "headers": self._headers(),
            "timeout": 30.0,
            "follow_redirects": True,
            "verify": False,
        }
        if self.proxy_manager is not None:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                kwargs["proxy"] = proxy
        try:
            return httpx.Client(http2=True, **kwargs)
        except Exception:
            kwargs.pop("http2", None)
            return httpx.Client(**kwargs)

    def gather(self) -> Dict[str, Any]:
        print(f"\n{C}[*]{N} جمع معلومات: @{self.username}\n")
        methods = [
            ("GraphQL API", self._try_graphql),
            ("Web Profile", self._try_web),
            ("HTML Scrape", self._try_html),
        ]
        for name, fn in methods:
            print(f"  {C}[→]{N} {name} ... ", end="", flush=True)
            try:
                data = fn()
                if data and data.get("exists"):
                    print(f"{G}OK{N}")
                    self.info.update(data)
                    self.info["exists"] = True
                    return self.info
                print(f"{Y}no data{N}")
            except Exception as e:
                print(f"{R}fail ({str(e)[:50]}){N}")
            time.sleep(0.7)
        self.info["exists"] = False
        return self.info

    def _try_graphql(self) -> Optional[Dict[str, Any]]:
        url = (
            "https://www.instagram.com/api/v1/users/web_profile_info/"
            f"?username={self.username}"
        )
        with self._client() as c:
            r = c.get(url)
            if r.status_code != 200:
                return None
            user = r.json().get("data", {}).get("user")
            if not user:
                return None
            return self._map_user(user, "graphql")

    def _try_web(self) -> Optional[Dict[str, Any]]:
        url = f"https://www.instagram.com/{self.username}/?__a=1&__d=1"
        with self._client() as c:
            r = c.get(url)
            if r.status_code != 200:
                return None
            try:
                data = r.json()
            except Exception:
                return None
            user = (data.get("graphql") or {}).get("user") or data.get("user")
            if not user:
                return None
            return self._map_user(user, "web_a1")

    def _try_html(self) -> Optional[Dict[str, Any]]:
        url = f"https://www.instagram.com/{self.username}/"
        with self._client() as c:
            r = c.get(url)
            html = r.text
            if r.status_code == 404 or "Sorry, this page" in html or "Page Not Found" in html:
                return {"exists": False}
            info: Dict[str, Any] = {"exists": True, "source": "html"}

            def grab(pat: str):
                m = re.search(pat, html)
                return m.group(1) if m else None

            fn = grab(r'"full_name":"([^"]*)"')
            if fn:
                info["full_name"] = fn.encode().decode("unicode_escape", errors="ignore")
            bio = grab(r'"biography":"([^"]*)"')
            if bio:
                info["biography"] = bio.encode().decode("unicode_escape", errors="ignore")
            for key, pat in [
                ("followers_count", r'"edge_followed_by":\{"count":(\d+)\}'),
                ("following_count", r'"edge_follow":\{"count":(\d+)\}'),
                ("posts_count", r'"edge_owner_to_timeline_media":\{"count":(\d+)\}'),
            ]:
                m = re.search(pat, html)
                if m:
                    info[key] = int(m.group(1))
            info["is_private"] = '"is_private":true' in html
            info["is_verified"] = '"is_verified":true' in html
            pic = grab(r'"profile_pic_url_hd":"([^"]+)"') or grab(
                r'"profile_pic_url":"([^"]+)"'
            )
            if pic:
                info["profile_pic"] = pic.replace("\\u0026", "&")
            i_id = grab(r'"id":"(\d+)"')
            if i_id:
                info["instagram_id"] = i_id
            return info

    def _map_user(self, user: dict, source: str) -> Dict[str, Any]:
        followers = 0
        following = 0
        posts = 0
        efb = user.get("edge_followed_by") or {}
        efl = user.get("edge_follow") or {}
        eot = user.get("edge_owner_to_timeline_media") or {}
        if isinstance(efb, dict):
            followers = efb.get("count", 0) or 0
        if isinstance(efl, dict):
            following = efl.get("count", 0) or 0
        if isinstance(eot, dict):
            posts = eot.get("count", 0) or 0
        followers = followers or user.get("follower_count", 0) or 0
        following = following or user.get("following_count", 0) or 0
        posts = posts or user.get("media_count", 0) or 0
        return {
            "exists": True,
            "full_name": user.get("full_name"),
            "biography": user.get("biography"),
            "followers_count": followers,
            "following_count": following,
            "posts_count": posts,
            "is_private": bool(user.get("is_private", False)),
            "is_verified": bool(user.get("is_verified", False)),
            "is_business": bool(
                user.get("is_business_account", False) or user.get("is_business", False)
            ),
            "business_category": user.get("business_category_name")
            or user.get("category_name"),
            "external_url": user.get("external_url"),
            "instagram_id": str(user.get("id") or user.get("pk") or ""),
            "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
            "source": source,
        }

    def save(self) -> Path:
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / "info.json"
        path.write_text(
            json.dumps(self.info, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{G}[✓]{N} حفظ: {path}")
        return path

    def display(self) -> None:
        print(f"\n{P}════ معلومات الحساب ════{N}")
        if not self.info.get("exists"):
            print(f"{R}[!] الحساب غير موجود{N}")
            return
        rows = [
            ("username", "المستخدم"),
            ("full_name", "الاسم"),
            ("biography", "البايو"),
            ("followers_count", "متابعون"),
            ("following_count", "يتابع"),
            ("posts_count", "منشورات"),
            ("is_private", "خاص"),
            ("is_verified", "موثق"),
            ("is_business", "تجاري"),
            ("business_category", "التصنيف"),
            ("external_url", "رابط"),
            ("instagram_id", "ID"),
            ("source", "المصدر"),
        ]
        for key, label in rows:
            val = self.info.get(key)
            if val in (None, "", False, 0, []):
                continue
            if isinstance(val, bool):
                val = "نعم" if valence else "لا"  # FIX - should be val
            if isinstance(val, bool):
                val = "نعم" if val else "لا"
            if isinstance(val, int):
                val = f"{val:,}"
            print(f"  {Y}{label}:{N} {W}{val}{N}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Info Gatherer")
    parser.add_argument("-u", "--username", required=True)
    args = parser.parse_args()
    proxy = None
    try:
        from modules.proxy_manager import ProxyManager

        proxy = ProxyManager()
    except Exception:
        pass
    g = InfoGatherer(args.username, proxy_manager=proxy)
    data = g.gather()
    if data.get("exists"):
        g.save()
        g.display()
    else:
        print(f"{R}فشل جمع المعلومات{N}")
        sys.exit(1)


if __name__ == "__main__":
    main()
