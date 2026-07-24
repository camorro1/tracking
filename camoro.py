#!/usr/bin/env python3
"""
Camoro v5.0 - AI-Powered Security Assessment Framework
Main CLI entrypoint
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

RESULTS_DIR = BASE_DIR / "results"
SESSIONS_DIR = BASE_DIR / "sessions"
MODULES_DIR = BASE_DIR / "modules"

for d in (RESULTS_DIR, SESSIONS_DIR, MODULES_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ensure package file
init_py = MODULES_DIR / "__init__.py"
if not init_py.exists():
    init_py.write_text('"""Camoro modules"""\n', encoding="utf-8")

from modules.brute_force import BruteForceEngine
from modules.info_gather import InfoGatherer
from modules.password_gen import PasswordGenerator
from modules.proxy_manager import ProxyManager
from modules.session_manager import SessionManager


class C:
    R = "\033[0;31m"
    G = "\033[0;32m"
    Y = "\033[1;33m"
    P = "\033[0;35m"
    C = "\033[0;36m"
    W = "\033[1;37m"
    N = "\033[0m"


def clear() -> None:
    os.system("clear" if os.name != "nt" else "cls")


def banner() -> None:
    clear()
    print(
        f"""{C.P}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗   ║
║  ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗  ║
║  ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║  ║
║  ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║  ║
║  ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝  ║
║   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ║
║                                                          ║
║     {C.W}v5.0 — AI Password Assessment Framework{C.P}           ║
║     {C.Y}Termux + Linux | Recon | Gen | Test | Tor{C.P}        ║
╚══════════════════════════════════════════════════════════╝{C.N}
"""
    )


def pause() -> None:
    input(f"\n{C.Y}[*] اضغط Enter للعودة...{C.N}")


def ask_user() -> str:
    u = input(f"{C.Y}اسم المستخدم (بدون @): {C.N}").strip().lstrip("@")
    return u


def ask_extra(info: dict) -> dict:
    print(f"\n{C.Y}[*] معلومات إضافية (Enter للتخطي){C.N}")
    fields = [
        ("real_name", "الاسم الحقيقي"),
        ("birthdate", "تاريخ الميلاد YYYY-MM-DD"),
        ("city", "المدينة"),
        ("partner_name", "اسم الشريك"),
        ("child_name", "اسم الطفل"),
        ("pet_name", "اسم الحيوان"),
        ("hobby", "الهواية"),
        ("fav_number", "رقم مفضل"),
        ("fav_color", "لون مفضل"),
        ("fav_team", "فريق"),
        ("fav_artist", "فنان"),
        ("keyword", "كلمة مفتاحية"),
        ("phone_last4", "آخر 4 من الهاتف"),
        ("old_password", "كلمة مرور قديمة"),
    ]
    for k, label in fields:
        v = input(f"  {label}: ").strip()
        if v:
            info[k] = v
    return info


def mode_intel() -> None:
    banner()
    print(f"{C.C}[1] جمع المعلومات{C.N}\n")
    u = ask_user()
    if not u:
        print(f"{C.R}مطلوب{C.N}")
        pause()
        return
    g = InfoGatherer(u, proxy_manager=ProxyManager())
    info = g.gather()
    if info and info.get("exists"):
        g.save()
        g.display()
        info = ask_extra(info)
        g.info = info
        g.save()
        print(f"{C.G}[✓] تم{C.N}")
    else:
        print(f"{C.R}[!] فشل / الحساب غير موجود{C.N}")
    pause()


def mode_gen() -> None:
    banner()
    print(f"{C.C}[2] توليد كلمات المرور{C.N}\n")
    u = ask_user()
    if not u:
        return
    path = RESULTS_DIR / u / "info.json"
    if path.exists():
        info = json.loads(path.read_text(encoding="utf-8"))
    else:
        print(f"{C.Y}[!] لا info.json — توليد أساسي فقط{C.N}")
        info = {"username": u}
    count_s = input(f"{C.Y}العدد (افتراضي 20000): {C.N}").strip()
    count = int(count_s) if count_s.isdigit() else 20000
    gen = PasswordGenerator(u, info)
    pw = gen.generate(count)
    gen.save(pw)
    print(f"\n{C.G}[✓] {len(pw):,} كلمة{C.N}")
    print(f"{C.C}عينة:{C.N}")
    for x in pw[:15]:
        print(f"  • {x}")
    pause()


def mode_attack() -> None:
    banner()
    print(f"{C.C}[3] اختبار كلمات المرور{C.N}\n")
    u = ask_user()
    if not u:
        return
    if not (RESULTS_DIR / u / "passwords.txt").exists():
        print(f"{C.R}[!] لا توجد passwords.txt — استخدم الخيار 2{C.N}")
        pause()
        return
    thr = input(f"{C.Y}threads (5): {C.N}").strip()
    rot = input(f"{C.Y}rotate every (3): {C.N}").strip()
    threads = int(thr) if thr.isdigit() else 5
    rotate = int(rot) if rot.isdigit() else 3
    print(f"{C.R}تحذير: للاختبار المصرّح فقط{C.N}")
    if input(f"{C.Y}اكتب YES للتأكيد: {C.N}").strip() != "YES":
        print("تم الإلغاء")
        pause()
        return
    eng = BruteForceEngine(
        u,
        proxy_manager=ProxyManager(),
        threads=threads,
        rotate_every=rotate,
    )
    eng.run()
    pause()


def mode_full() -> None:
    banner()
    print(f"{C.C}[4] الوضع الكامل{C.N}\n")
    u = ask_user()
    if not u:
        return

    print(f"\n{C.C}[1/3] جمع المعلومات...{C.N}")
    g = InfoGatherer(u, proxy_manager=ProxyManager())
    info = g.gather()
    if not info or not info.get("exists"):
        # نستمر حتى لو فشل — نستخدم الاسم فقط
        print(f"{C.Y}[!] الجمع فشل — متابعة بالحد الأدنى{C.N}")
        info = {"username": u, "exists": True}
    else:
        g.display()
    info = ask_extra(info)
    g.info = info
    g.save()

    print(f"\n{C.C}[2/3] توليد 20000 كلمة...{C.N}")
    gen = PasswordGenerator(u, info)
    pw = gen.generate(20000)
    gen.save(pw)
    print(f"{C.G}[✓] {len(pw):,}{C.N}")

    if input(f"\n{C.Y}بدء الاختبار؟ YES: {C.N}").strip() != "YES":
        print("تم الحفظ بدون اختبار")
        pause()
        return

    print(f"\n{C.C}[3/3] الاختبار...{C.N}")
    BruteForceEngine(u, proxy_manager=ProxyManager(), threads=5, rotate_every=3).run()
    pause()


def mode_results() -> None:
    banner()
    print(f"{C.C}[5] النتائج{C.N}\n")
    dirs = sorted([d for d in RESULTS_DIR.iterdir() if d.is_dir()]) if RESULTS_DIR.exists() else []
    if not dirs:
        print("لا توجد نتائج")
        pause()
        return
    for d in dirs:
        ok = (d / "success.txt").exists() or (d / "FOUND.txt").exists()
        pwd_n = 0
        p = d / "passwords.txt"
        if p.exists():
            pwd_n = sum(1 for _ in p.open(encoding="utf-8", errors="ignore"))
        tested_n = 0
        t = d / "tested.txt"
        if t.exists():
            tested_n = sum(1 for _ in t.open(encoding="utf-8", errors="ignore"))
        st = f"{C.G}SUCCESS{C.N}" if ok else f"{C.Y}PENDING{C.N}"
        print(f"  • {d.name} | {st} | pw={pwd_n} tested={tested_n}")
        if ok:
            sp = d / "success.txt"
            if sp.exists():
                print(sp.read_text(encoding="utf-8", errors="ignore"))
            else:
                print((d / "FOUND.txt").read_text(encoding="utf-8", errors="ignore"))
        print()
    pause()


def mode_proxy() -> None:
    banner()
    print(f"{C.C}[6] Proxy / Tor{C.N}\n")
    pm = ProxyManager()
    print("  1) حالة Tor")
    print("  2) تغيير IP")
    print("  3) اختبار الاتصال")
    print("  4) IP الحالي")
    ch = input(f"\n{C.Y}> {C.N}").strip()
    if ch == "1":
        print("Tor:", f"{C.G}ON{C.N}" if pm.check_tor() else f"{C.R}OFF{C.N}")
        print("rotations:", pm.total_rotations)
    elif ch == "2":
        print(pm.rotate_ip())
    elif ch == "3":
        print(pm.test_connection())
    elif ch == "4":
        print(pm.get_current_ip())
    pause()


def mode_session() -> None:
    banner()
    print(f"{C.C}[7] Sessions{C.N}\n")
    sm = SessionManager()
    print("  1) حفظ")
    print("  2) تحميل")
    print("  3) عرض الكل")
    print("  4) حذف")
    ch = input(f"\n{C.Y}> {C.N}").strip()
    if ch == "1":
        u = input("username: ").strip()
        sid = input("session_id: ").strip()
        csrf = input("csrf: ").strip()
        sm.save(u, sid, csrf)
        print(f"{C.G}OK{C.N}")
    elif ch == "2":
        print(sm.load(input("username: ").strip()))
    elif ch == "3":
        items = sm.list_all()
        if not items:
            print("فارغ")
        for s in items:
            print(f"  • {s.get('username')} | {s.get('created_at')}")
    elif ch == "4":
        print("deleted" if sm.delete(input("username: ").strip()) else "not found")
    pause()


def main() -> None:
    signal.signal(signal.SIGINT, lambda *_: (print(f"\n{C.Y}خروج{C.N}"), sys.exit(0)))
    actions = {
        "1": mode_intel,
        "2": mode_gen,
        "3": mode_attack,
        "4": mode_full,
        "5": mode_results,
        "6": mode_proxy,
        "7": mode_session,
    }
    while True:
        banner()
        print(f"  {C.C}[1]{C.N} 🔍  جمع معلومات")
        print(f"  {C.C}[2]{C.N} 🧠  توليد كلمات مرور")
        print(f"  {C.C}[3]{C.N} ⚡  اختبار")
        print(f"  {C.C}[4]{C.N} 🔄  وضع كامل")
        print(f"  {C.C}[5]{C.N} 📊  النتائج")
        print(f"  {C.C}[6]{C.N} 🌐  Proxy/Tor")
        print(f"  {C.C}[7]{C.N} 🔑  Sessions")
        print(f"  {C.C}[0]{C.N} 🚪  خروج")
        ch = input(f"\n  {C.Y}اختيارك: {C.N}").strip()
        if ch == "0":
            print(f"{C.G}مع السلامة{C.N}")
            break
        fn = actions.get(ch)
        if fn:
            try:
                fn()
            except Exception as e:
                print(f"{C.R}[!] خطأ: {e}{C.N}")
                pause()
        else:
            print(f"{C.R}خيار غير صحيح{C.N}")
            time.sleep(0.8)


if __name__ == "__main__":
    main()
