#!/usr/bin/env python3
"""Camoro - AI Password Generator"""

import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
RESULTS_DIR = BASE_DIR / "results"

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
WHITE = "\033[1;37m"
NC = "\033[0m"


class PasswordGenerator:
    def __init__(self, username, info=None):
        self.username = username.strip().lstrip("@").lower()
        self.info = info or {}
        self.passwords = set()

    def _keywords(self):
        keys = set()
        keys.add(self.username)
        for field in [
            "full_name", "real_name", "city", "partner_name", "child_name",
            "pet_name", "hobby", "fav_color", "fav_team", "fav_artist",
            "fav_food", "keyword", "keyword1", "keyword2", "keyword3"
        ]:
            val = self.info.get(field)
            if not val:
                continue
            for part in str(val).replace("-", " ").split():
                part = part.strip().lower()
                if len(part) >= 2:
                    keys.add(part)
                    keys.add(part.capitalize())
        bio = self.info.get("biography") or ""
        for w in re.findall(r"\w{3,}", bio.lower()):
            if w not in {"the", "and", "for", "with", "this", "from", "instagram"}:
                keys.add(w)
        return list(keys)

    def _suffixes(self):
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        nums = [
            "1", "12", "123", "1234", "12345", "123456", "007", "111", "420",
            "69", "77", "99", "100", "777", "000", "1111", "2020", "2021",
            "2022", "2023", "2024", "2025", "2026", "!", "@", "#", "123!", "123@"
        ]
        bd = self.info.get("birthdate") or self.info.get("birthday") or ""
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", bd)
        extra = []
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            extra += [y, y[2:], f"{d}{mo}{y}", f"{d}{mo}{y[2:]}", f"{mo}{d}{y}", f"{y}{mo}{d}"]
        if self.info.get("fav_number"):
            extra.append(str(self.info["fav_number"]))
        return list(dict.fromkeys(extra + years + nums))

    def generate(self, target_count=20000):
        print(f"\n{CYAN}[*]{NC} توليد كلمات المرور...\n")
        kws = self._keywords()
        sfx = self._suffixes()

        # 1 basic
        for k in kws:
            self.passwords.add(k)
            for s in sfx[:40]:
                self.passwords.add(f"{k}{s}")
                self.passwords.add(f"{s}{k}")
                self.passwords.add(f"{k}_{s}")

        # 2 name combos
        for i, a in enumerate(kws[:12]):
            for b in kws[i + 1:12]:
                self.passwords.update([f"{a}{b}", f"{b}{a}", f"{a}_{b}", f"{a}.{b}"])

        # 3 common
        common = [
            "password", "123456", "12345678", "qwerty", "abc123", "iloveyou",
            "admin", "welcome", "instagram", "insta123", "love", "baby",
            "ahmed", "mohamed", "sara", "nour", "ali", "omar"
        ]
        self.passwords.update(common)

        # 4 instagram patterns
        for p in [
            f"insta{self.username}", f"{self.username}insta",
            f"ig_{self.username}", f"{self.username}_ig",
            f"gram{self.username}", f"{self.username}gram"
        ]:
            self.passwords.update([p, p + "1", p + "123", p + "!"])

        # 5 leet + case
        leet = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
        base = list(self.passwords)[:8000]
        for pwd in base:
            self.passwords.add(pwd.lower())
            self.passwords.add(pwd.upper())
            self.passwords.add(pwd.capitalize())
            self.passwords.add(pwd + "!")
            self.passwords.add("!" + pwd)
            lp = "".join(leet.get(c.lower(), c) for c in pwd)
            if lp != pwd:
                self.passwords.add(lp)

        # filter
        valid = [p for p in self.passwords if isinstance(p, str) and 4 <= len(p.strip()) <= 64]
        valid = list(set(valid))
        random.shuffle(valid)

        if len(valid) < target_count:
            more = []
            for p in valid[:5000]:
                for s in sfx[:20]:
                    more.append(f"{p}{s}")
                    if len(valid) + len(more) >= target_count:
                        break
                if len(valid) + len(more) >= target_count:
                    break
            valid.extend(more)

        valid = list(dict.fromkeys(valid))[:target_count]
        random.shuffle(valid)
        print(f"{GREEN}[✓]{NC} تم توليد {len(valid):,} كلمة مرور")
        return valid

    def save(self, passwords):
        user_dir = RESULTS_DIR / self.username
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / "passwords.txt"
        with open(path, "w", encoding="utf-8") as f:
            for p in passwords:
                f.write(str(p).strip() + "\n")
        print(f"{GREEN}[✓]{NC} حفظ: {path}")
        return path


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--username", "-u", required=True)
    p.add_argument("--count", "-c", type=int, default=20000)
    args = p.parse_args()

    info_path = RESULTS_DIR / args.username / "info.json"
    if not info_path.exists():
        print("لا توجد معلومات. شغّل info_gather أولاً")
        sys.exit(1)
    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    gen = PasswordGenerator(args.username, info)
    pwds = gen.generate(args.count)
    gen.save(pwds)
