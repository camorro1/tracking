#!/usr/bin/env python3
"""Camoro - Information Gathering (fixed working recon)"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    raise SystemExit("[!] pip install httpx") from None

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

R = "\033[0;31m"
G = "\033[0;32m"
Y = "\033[1;33m"
C = "\033[0;36m"
W = "\033[1;37m"
P = "\033[0;35m"
N = "\033[0m"

# App-ID الرسمي لواجهة الويب العامة
IG_APP_ID = "936619743392459"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


class InfoGatherer:
    def __init__(self, username: str, proxy_manager: Any = None, use_proxy: bool = False) -> None:
        """
        use_proxy=False افتراضياً لأن Tor غالباً كيعلق recon على Instagram.
        فعّله فقط إذا احتاجيت IP rotation.
        """
        self.username = username.strip().lstrip("@").lower()
        self.proxy_manager = proxy_manager
        self.use_proxy = use_proxy
        self.info: Dict[str, Any] = {
            "username": self.username,
            "exists": False,
            "user_id": None,
            "instagram_id": None,
            "full_name": "",
            "biography": "",
            "external_url": "",
            "is_private": None,
            "is_verified": None,
            "is_business": None,
            "followers": 0,
            "following": 0,
            "posts": 0,
            "followers_count": 0,
            "following_count": 0,
            "posts_count": 0,
            "profile_pic_url": "",
            "profile_pic": "",
            "category": "",
            "business_category": "",
            "public_email": "",
            "public_phone": "",
            "keywords": [],
            "possible_names": [],
            "years_found": [],
            "source": "",
            "gathered_at": "",
            "collected_at": "",
        }
        self.user_dir = RESULTS_DIR / self.username
        self.user_dir.mkdir(parents=True, exist_ok=True)

    def _headers(self, api: bool = False) -> Dict[str, str]:
        h = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.instagram.com/",
            "Origin": "https://www.instagram.com",
            "X-IG-App-ID": IG_APP_ID,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        }
        if api:
            h["Accept"] = "*/*"
            h["X-Requested-With"] = "XMLHttpRequest"
        else:
            h["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        return h

    def _make_client(self, timeout: float = 15.0) -> httpx.Client:
        kwargs: Dict[str, Any] = {
            "headers": self._headers(api=True),
            "timeout": httpx.Timeout(timeout, connect=8.0),
            "follow_redirects": True,
            "verify": False,
        }
        if self.use_proxy and self.proxy_manager is not None:
            try:
                p = self.proxy_manager.get_proxy()
                if p:
                    kwargs["proxy"] = p
                    print(f"  {Y}[proxy]{N} {p}")
            except Exception:
                pass
        return httpx.Client(**kwargs)

    @staticmethod
    def _count(val: Any) -> int:
        try:
            if val is None:
                return 0
            if isinstance(val, dict):
                val = val.get("count", 0)
            return int(val or 0)
        except Exception:
            return 0

    def _apply_user(self, user: dict, source: str) -> bool:
        if not user or not isinstance(user, dict):
            return False

        uid = user.get("id") or user.get("pk") or user.get("pk_id")
        uname = (user.get("username") or "").lower()
        if uname and uname != self.username:
            # مش الحساب المطلوب
            if not uid:
                return False

        followers = self._count(
            user.get("edge_followed_by")
            or user.get("follower_count")
            or user.get("followers")
        )
        following = self._count(
            user.get("edge_follow")
            or user.get("following_count")
            or user.get("following")
        )
        posts = self._count(
            user.get("edge_owner_to_timeline_media")
            or user.get("media_count")
            or user.get("posts")
        )

        full_name = user.get("full_name") or ""
        bio = user.get("biography") or ""
        pic = (
            user.get("profile_pic_url_hd")
            or user.get("profile_pic_url")
            or ""
        )
        if isinstance(user.get("hd_profile_pic_url_info"), dict):
            pic = user["hd_profile_pic_url_info"].get("url") or pic

        self.info.update(
            {
                "exists": True,
                "user_id": str(uid) if uid else self.info.get("user_id"),
                "instagram_id": str(uid) if uid else self.info.get("instagram_id"),
                "full_name": full_name or self.info.get("full_name") or "",
                "biography": bio or self.info.get("biography") or "",
                "external_url": user.get("external_url")
                or self.info.get("external_url")
                or "",
                "is_private": user.get("is_private"),
                "is_verified": user.get("is_verified"),
                "is_business": bool(
                    user.get("is_business_account")
                    or user.get("is_business")
                    or user.get("is_professional_account")
                ),
                "followers": followers,
                "following": following,
                "posts": posts,
                "followers_count": followers,
                "following_count": following,
                "posts_count": posts,
                "profile_pic_url": str(pic) if pic else "",
                "profile_pic": str(pic) if pic else "",
                "category": user.get("category_name")
                or user.get("business_category_name")
                or "",
                "business_category": user.get("business_category_name")
                or user.get("category_name")
                or "",
                "public_email": user.get("business_email")
                or user.get("public_email")
                or "",
                "public_phone": user.get("business_phone_number")
                or user.get("contact_phone_number")
                or user.get("public_phone_number")
                or "",
                "source": source,
            }
        )
        return True

    # ─────────────────────────────────────────────
    # Method 1: i.instagram.com (الأقوى حالياً)
    # ─────────────────────────────────────────────
    def method_ios_api(self) -> bool:
        print(f"  {C}[1/5]{N} i.instagram API ...", end=" ", flush=True)
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        try:
            with self._make_client(12.0) as client:
                # تسخين session (cookies)
                try:
                    client.get("https://www.instagram.com/", headers=self._headers(False))
                except Exception:
                    pass
                r = client.get(url, headers=self._headers(True))
                if r.status_code == 404:
                    print(f"{R}not found{N}")
                    self.info["exists"] = False
                    return False
                if r.status_code != 200:
                    print(f"{Y}HTTP {r.status_code}{N}")
                    return False
                data = r.json()
                user = (data.get("data") or {}).get("user")
                if not user:
                    print(f"{Y}empty{N}")
                    return False
                ok = self._apply_user(user, "i.instagram.com/web_profile_info")
                print(f"{G}OK{N}" if ok else f"{Y}empty{N}")
                return ok
        except httpx.TimeoutException:
            print(f"{R}timeout{N}")
            return False
        except Exception as e:
            print(f"{R}{type(e).__name__}{N}")
            return False

    # ─────────────────────────────────────────────
    # Method 2: www web_profile_info
    # ─────────────────────────────────────────────
    def method_web_api(self) -> bool:
        print(f"  {C}[2/5]{N} www web API ...", end=" ", flush=True)
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        try:
            with self._make_client(12.0) as client:
                try:
                    client.get("https://www.instagram.com/")
                except Exception:
                    pass
                r = client.get(url, headers=self._headers(True))
                if r.status_code != 200:
                    print(f"{Y}HTTP {r.status_code}{N}")
                    return False
                user = (r.json().get("data") or {}).get("user")
                if not user:
                    print(f"{Y}empty{N}")
                    return False
                ok = self._apply_user(user, "www/web_profile_info")
                print(f"{G}OK{N}" if ok else f"{Y}empty{N}")
                return ok
        except httpx.TimeoutException:
            print(f"{R}timeout{N}")
            return False
        except Exception as e:
            print(f"{R}{type(e).__name__}{N}")
            return False

    # ─────────────────────────────────────────────
    # Method 3: HTML + meta + shared JSON
    # ─────────────────────────────────────────────
    def method_html(self) -> bool:
        print(f"  {C}[3/5]{N} HTML scrape ...", end=" ", flush=True)
        url = f"https://www.instagram.com/{self.username}/"
        try:
            with self._make_client(15.0) as client:
                r = client.get(url, headers=self._headers(False))
                if r.status_code == 404:
                    print(f"{R}not found{N}")
                    self.info["exists"] = False
                    return False
                if r.status_code != 200:
                    print(f"{Y}HTTP {r.status_code}{N}")
                    return False

                html = r.text
                if "Sorry, this page isn't available" in html:
                    print(f"{R}not found{N}")
                    self.info["exists"] = False
                    return False

                # 1) _sharedData
                m = re.search(
                    r"window\._sharedData\s*=\s*(\{.+?\});\s*</script>",
                    html,
                    re.DOTALL,
                )
                if m:
                    try:
                        data = json.loads(m.group(1))
                        user = (
                            data.get("entry_data", {})
                            .get("ProfilePage", [{}])[0]
                            .get("graphql", {})
                            .get("user")
                        )
                        if user and self._apply_user(user, "html_sharedData"):
                            print(f"{G}OK{N}")
                            return True
                    except Exception:
                        pass

                # 2) JSON blobs داخل script type="application/json"
                for m in re.finditer(
                    r'<script[^>]*type="application/json"[^>]*>(\{.*?\})</script>',
                    html,
                    re.DOTALL,
                ):
                    try:
                        blob = m.group(1)
                        if "follower" not in blob and "full_name" not in blob:
                            continue
                        # ابحث عن user object
                        um = re.search(
                            r'"user"\s*:\s*(\{(?:[^{}]|\{[^{}]*\})*\})',
                            blob,
                        )
                        # fallback: parse whole and walk
                        data = json.loads(blob)
                        user = self._find_user_dict(data)
                        if user and self._apply_user(user, "html_app_json"):
                            print(f"{G}OK{N}")
                            return True
                    except Exception:
                        continue

                # 3) meta tags (og:description فيه المتابعين)
                info_got = False
                og_title = self._meta(html, "og:title")
                og_desc = self._meta(html, "og:description") or self._meta(html, "description")
                og_image = self._meta(html, "og:image")

                if og_title:
                    # "Name (@user) • Instagram photos and videos"
                    name = re.sub(r"\s*\(@[^)]+\).*", "", og_title).strip()
                    name = re.sub(r"\s*[•·].*", "", name).strip()
                    if name and "instagram" not in name.lower():
                        self.info["full_name"] = name
                        info_got = True

                if og_desc:
                    # "1,234 Followers, 56 Following, 7 Posts - Bio here"
                    cm = re.search(
                        r"([\d,\.]+[KkMm]?)\s*Followers?,\s*([\d,\.]+[KkMm]?)\s*Following,\s*([\d,\.]+[KkMm]?)\s*Posts?",
                        og_desc,
                        re.I,
                    )
                    if cm:
                        self.info["followers"] = self._parse_human(cm.group(1))
                        self.info["following"] = self._parse_human(cm.group(2))
                        self.info["posts"] = self._parse_human(cm.group(3))
                        self.info["followers_count"] = self.info["followers"]
                        self.info["following_count"] = self.info["following"]
                        self.info["posts_count"] = self.info["posts"]
                        bio = re.sub(
                            r"^[\d,\.]+[KkMm]?\s*Followers?,\s*[\d,\.]+[KkMm]?\s*Following,\s*[\d,\.]+[KkMm]?\s*Posts?\s*[-–—:]?\s*",
                            "",
                            og_desc,
                            flags=re.I,
                        ).strip()
                        if bio:
                            self.info["biography"] = bio
                        info_got = True
                    elif not self.info.get("biography"):
                        self.info["biography"] = og_desc
                        info_got = True

                if og_image:
                    self.info["profile_pic_url"] = og_image
                    self.info["profile_pic"] = og_image
                    info_got = True

                # regex fallbacks
                for key, pat in [
                    ("full_name", r'"full_name"\s*:\s*"([^"]*)"'),
                    ("biography", r'"biography"\s*:\s*"((?:[^"\\]|\\.)*)"'),
                    ("user_id", r'"profilePage_(\d+)"'),
                    ("user_id", r'"id"\s*:\s*"(\d+)"'),
                ]:
                    mm = re.search(pat, html)
                    if mm and not self.info.get(key):
                        val = mm.group(1)
                        if key == "biography":
                            try:
                                val = json.loads(f'"{val}"')
                            except Exception:
                                val = val.encode().decode("unicode_escape", errors="ignore")
                        self.info[key] = val
                        if key == "user_id":
                            self.info["instagram_id"] = val
                        info_got = True

                for key, pat in [
                    ("followers", r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)'),
                    ("following", r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)'),
                    ("posts", r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)'),
                    ("followers", r'"follower_count"\s*:\s*(\d+)'),
                    ("following", r'"following_count"\s*:\s*(\d+)'),
                    ("posts", r'"media_count"\s*:\s*(\d+)'),
                ]:
                    mm = re.search(pat, html)
                    if mm:
                        self.info[key] = int(mm.group(1))
                        self.info[f"{key}_count" if key != "posts" else "posts_count"] = int(
                            mm.group(1)
                        )
                        if key == "posts":
                            self.info["posts_count"] = int(mm.group(1))
                        if key == "followers":
                            self.info["followers_count"] = int(mm.group(1))
                        if key == "following":
                            self.info["following_count"] = int(mm.group(1))
                        info_got = True

                if '"is_private":true' in html or '"is_private": true' in html:
                    self.info["is_private"] = True
                elif '"is_private":false' in html or '"is_private": false' in html:
                    self.info["is_private"] = False

                if info_got:
                    self.info["exists"] = True
                    self.info["source"] = "html_meta"
                    print(f"{G}OK{N}")
                    return True

                print(f"{Y}no data{N}")
                return False
        except httpx.TimeoutException:
            print(f"{R}timeout{N}")
            return False
        except Exception as e:
            print(f"{R}{type(e).__name__}{N}")
            return False

    def _find_user_dict(self, obj: Any, depth: int = 0) -> Optional[dict]:
        if depth > 8:
            return None
        if isinstance(obj, dict):
            # signature of IG user object
            if (
                ("username" in obj or "full_name" in obj)
                and (
                    "edge_followed_by" in obj
                    or "follower_count" in obj
                    or "biography" in obj
                )
            ):
                un = str(obj.get("username", "")).lower()
                if not un or un == self.username:
                    return obj
            for v in obj.values():
                found = self._find_user_dict(v, depth + 1)
                if found:
                    return found
        elif isinstance(obj, list):
            for item in obj[:50]:
                found = self._find_user_dict(item, depth + 1)
                if found:
                    return found
        return None

    @staticmethod
    def _meta(html: str, prop: str) -> str:
        m = re.search(
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']*)["\']',
            html,
            re.I,
        )
        if not m:
            m = re.search(
                rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']{re.escape(prop)}["\']',
                html,
                re.I,
            )
        if not m:
            return ""
        return (
            m.group(1)
            .replace("&amp;", "&")
            .replace("&#064;", "@")
            .replace("&quot;", '"')
            .strip()
        )

    @staticmethod
    def _parse_human(s: str) -> int:
        s = (s or "").strip().lower().replace(",", "").replace(" ", "")
        try:
            if s.endswith("k"):
                return int(float(s[:-1]) * 1000)
            if s.endswith("m"):
                return int(float(s[:-1]) * 1_000_000)
            return int(float(s))
        except Exception:
            return 0

    # ─────────────────────────────────────────────
    # Method 4: Embed
    # ─────────────────────────────────────────────
    def method_embed(self) -> bool:
        print(f"  {C}[4/5]{N} Embed page ...", end=" ", flush=True)
        url = f"https://www.instagram.com/{self.username}/embed/"
        try:
            with self._make_client(12.0) as client:
                r = client.get(url, headers=self._headers(False))
                if r.status_code != 200:
                    print(f"{Y}HTTP {r.status_code}{N}")
                    return False
                html = r.text
                got = False
                m = re.search(r'"full_name"\s*:\s*"([^"]*)"', html)
                if m and m.group(1):
                    self.info["full_name"] = (
                        m.group(1).encode().decode("unicode_escape", errors="ignore")
                    )
                    got = True
                m = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
                if m:
                    self.info["followers"] = int(m.group(1))
                    self.info["followers_count"] = int(m.group(1))
                    got = True
                m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
                if m:
                    self.info["following"] = int(m.group(1))
                    self.info["following_count"] = int(m.group(1))
                    got = True
                m = re.search(
                    r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html
                )
                if m:
                    self.info["posts"] = int(m.group(1))
                    self.info["posts_count"] = int(m.group(1))
                    got = True
                m = re.search(r'"biography"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
                if m:
                    try:
                        self.info["biography"] = json.loads(f'"{m.group(1)}"')
                    except Exception:
                        self.info["biography"] = m.group(1)
                    got = True
                m = re.search(r'"id"\s*:\s*"(\d+)"', html)
                if m:
                    self.info["user_id"] = m.group(1)
                    self.info["instagram_id"] = m.group(1)
                    got = True
                m = re.search(r'"is_private"\s*:\s*(true|false)', html)
                if m:
                    self.info["is_private"] = m.group(1) == "true"
                m = re.search(r'"is_verified"\s*:\s*(true|false)', html)
                if m:
                    self.info["is_verified"] = m.group(1) == "true"

                if got:
                    self.info["exists"] = True
                    self.info["source"] = "embed"
                    print(f"{G}OK{N}")
                    return True
                print(f"{Y}no data{N}")
                return False
        except httpx.TimeoutException:
            print(f"{R}timeout{N}")
            return False
        except Exception as e:
            print(f"{R}{type(e).__name__}{N}")
            return False

    # ─────────────────────────────────────────────
    # Method 5: Topsearch
    # ─────────────────────────────────────────────
    def method_topsearch(self) -> bool:
        print(f"  {C}[5/5]{N} TopSearch ...", end=" ", flush=True)
        url = "https://www.instagram.com/web/search/topsearch/"
        try:
            with self._make_client(10.0) as client:
                r = client.get(
                    url,
                    params={"query": self.username, "context": "blended"},
                    headers=self._headers(True),
                )
                if r.status_code != 200:
                    print(f"{Y}HTTP {r.status_code}{N}")
                    return False
                for item in r.json().get("users", []):
                    u = item.get("user") or item
                    if (u.get("username") or "").lower() == self.username:
                        self.info["exists"] = True
                        self.info["user_id"] = str(u.get("pk") or u.get("id") or "")
                        self.info["instagram_id"] = self.info["user_id"]
                        self.info["full_name"] = u.get("full_name") or self.info.get("full_name") or ""
                        self.info["is_private"] = u.get("is_private")
                        self.info["is_verified"] = u.get("is_verified")
                        self.info["profile_pic_url"] = u.get("profile_pic_url") or ""
                        self.info["profile_pic"] = self.info["profile_pic_url"]
                        # topsearch ما كيعطيش followers دائماً — مكملش لو عندنا numbers
                        if not self.info.get("source") or self.info["source"] == "":
                            self.info["source"] = "topsearch"
                        print(f"{G}OK{N}")
                        return True
                print(f"{Y}no match{N}")
                return False
        except httpx.TimeoutException:
            print(f"{R}timeout{N}")
            return False
        except Exception as e:
            print(f"{R}{type(e).__name__}{N}")
            return False

    def _extract_keywords(self) -> None:
        text = " ".join(
            str(self.info.get(k) or "")
            for k in ("full_name", "biography", "username", "category", "external_url")
        )
        words = re.findall(r"[A-Za-z\u0600-\u06FF]{3,}", text)
        seen = set()
        kws: List[str] = []
        for w in words:
            wl = w.lower()
            if wl not in seen and wl != self.username:
                seen.add(wl)
                kws.append(w)
        self.info["keywords"] = kws[:40]

        names: List[str] = []
        full = (self.info.get("full_name") or "").strip()
        if full:
            names.append(full)
            for p in re.split(r"[\s_\-\.]+", full):
                if len(p) >= 2:
                    names.append(p)
        for p in re.split(r"[._\-]+", self.username):
            if len(p) >= 2:
                names.append(p)
        self.info["possible_names"] = list(dict.fromkeys(names))[:25]
        self.info["years_found"] = list(
            dict.fromkeys(re.findall(r"\b(19[8-9]\d|20[0-3]\d)\b", text))
        )

    def gather(self) -> Dict[str, Any]:
        print(f"\n{C}[*]{N} جمع معلومات @{self.username}")
        print(f"  {Y}mode:{N} {'proxy/tor' if self.use_proxy else 'direct (أسرع)'}")
        print()

        methods = [
            self.method_ios_api,
            self.method_web_api,
            self.method_html,
            self.method_embed,
            self.method_topsearch,
        ]

        for fn in methods:
            try:
                ok = fn()
            except Exception as e:
                print(f"  {R}error: {e}{N}")
                ok = False

            # نجاح كامل = عندنا followers أو full_name على الأقل
            if ok and self.info.get("exists"):
                if (
                    self.info.get("followers")
                    or self.info.get("full_name")
                    or self.info.get("user_id")
                ):
                    # إذا جينا من topsearch بلا أرقام .كمّل المحاولات
                    if self.info.get("source") == "topsearch" and not self.info.get("followers"):
                        time.sleep(0.5)
                        continue
                    break
            time.sleep(random.uniform(0.3, 0.8))

        now = datetime.now().isoformat()
        self.info["gathered_at"] = now
        self.info["collected_at"] = now

        if self.info.get("exists"):
            self._extract_keywords()
            print(f"\n{G}[✓]{N} تم التحليل بنجاح (source={self.info.get('source')})")
        else:
            print(f"\n{R}[!]{N} فشل التحليل — الحساب غير موجود أو Instagram حاجب الـ IP")
            print(f"  {Y}جرّب:{N} شبكة أخرى / VPN / عطّل Tor / بدّل IP")

        return self.info

    def save(self, path: Optional[Path] = None) -> Path:
        out = path or (self.user_dir / "info.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.info, indent=2, ensure_ascii=False), encoding="utf-8")

        txt = self.user_dir / "info.txt"
        lines = [
            f"Username  : @{self.info.get('username')}",
            f"Exists    : {self.info.get('exists')}",
            f"User ID   : {self.info.get('user_id')}",
            f"Full Name : {self.info.get('full_name')}",
            f"Bio       : {self.info.get('biography')}",
            f"Followers : {self.info.get('followers')}",
            f"Following : {self.info.get('following')}",
            f"Posts     : {self.info.get('posts')}",
            f"Private   : {self.info.get('is_private')}",
            f"Verified  : {self.info.get('is_verified')}",
            f"Business  : {self.info.get('is_business')}",
            f"Website   : {self.info.get('external_url')}",
            f"Email     : {self.info.get('public_email')}",
            f"Phone     : {self.info.get('public_phone')}",
            f"Category  : {self.info.get('category')}",
            f"Keywords  : {', '.join(self.info.get('keywords') or [])}",
            f"Source    : {self.info.get('source')}",
            f"Time      : {self.info.get('gathered_at')}",
        ]
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{G}[✓]{N} حفظ: {out}")
        return out

    def display(self) -> None:
        i = self.info
        print(f"\n{P}╔══════════════════════════════════════╗{N}")
        print(f"{P}║{N}     {W}تحليل الحساب — Camoro Recon{N}      {P}║{N}")
        print(f"{P}╚══════════════════════════════════════╝{N}")

        if not i.get("exists"):
            print(f"{R}  [!] الحساب غير موجود أو محجوب{N}\n")
            return

        def row(label: str, val: Any) -> None:
            if val is None or val == "" or val == []:
                val = "-"
            if isinstance(val, bool):
                val = f"{G}نعم{N}" if val else f"{R}لا{N}"
            if isinstance(val, int):
                val = f"{val:,}"
            print(f"  {C}{label:<12}{N} {W}{val}{N}")

        row("المستخدم", f"@{i.get('username')}")
        row("الاسم", i.get("full_name"))
        row("البايو", (i.get("biography") or "-")[:80])
        row("المتابعون", i.get("followers"))
        row("يتابع", i.get("following"))
        row("المنشورات", i.get("posts"))
        row("خاص", i.get("is_private"))
        row("موثّق", i.get("is_verified"))
        row("تجاري", i.get("is_business"))
        row("ID", i.get("user_id"))
        row("الموقع", i.get("external_url"))
        row("التصنيف", i.get("category"))
        row("المصدر", i.get("source"))
        if i.get("keywords"):
            row("كلمات", ", ".join((i.get("keywords") or [])[:8]))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Camoro Info Gatherer")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("--proxy", action="store_true", help="استخدم Tor/Proxy (أبطأ)")
    args = parser.parse_args()

    proxy = None
    if args.proxy:
        try:
            sys.path.insert(0, str(BASE_DIR))
            from modules.proxy_manager import ProxyManager

            proxy = ProxyManager()
        except Exception:
            proxy = None

    g = InfoGatherer(args.username, proxy_manager=proxy, use_proxy=args.proxy)
    g.gather()
    g.save()
    g.display()
    sys.exit(0 if g.info.get("exists") else 1)


if __name__ == "__main__":
    main()
