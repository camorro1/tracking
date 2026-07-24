#!/usr/bin/env python3
"""Camoro - Proxy / Tor Manager"""

from __future__ import annotations

import random
import socket
import subprocess
import threading
import time
from typing import Dict, List, Optional

try:
    import httpx
except ImportError as e:
    raise SystemExit("[!] pip install httpx[socks]") from e


class ProxyManager:
    def __init__(self) -> None:
        self.current_ip: Optional[str] = None
        self.total_rotations: int = 0
        self.request_count: int = 0
        self.proxy_list: List[str] = []
        self.lock = threading.Lock()
        self._tor_ok: Optional[bool] = None

    def check_tor(self) -> bool:
        try:
            which = subprocess.run(
                ["which", "tor"], capture_output=True, text=True, timeout=5
            )
            if which.returncode != 0:
                self._tor_ok = False
                return False
            with httpx.Client(proxy="socks5://127.0.0.1:9050", timeout=8.0) as c:
                r = c.get("https://api.ipify.org")
                self._tor_ok = r.status_code == 200
                return self._tor_ok
        except Exception:
            self._tor_ok = False
            return False

    def get_current_ip(self) -> Optional[str]:
        try:
            kwargs: dict = {"timeout": 10.0}
            if self.check_tor():
                kwargs["proxy"] = "socks5://127.0.0.1:9050"
            with httpx.Client(**kwargs) as c:
                r = c.get("https://api.ipify.org?format=json")
                if r.status_code == 200:
                    self.current_ip = r.json().get("ip")
                    return self.current_ip
        except Exception:
            pass
        return None

    def rotate_ip(self) -> Optional[str]:
        with self.lock:
            print("\n[*] جاري تغيير IP...")
            try:
                s = socket.socket()
                s.settimeout(5)
                s.connect(("127.0.0.1", 9051))
                s.sendall(b"AUTHENTICATE\r\n")
                resp = s.recv(1024)
                if b"250" in resp:
                    s.sendall(b"SIGNAL NEWNYM\r\n")
                    s.recv(1024)
                    time.sleep(2.5)
                s.close()
                with httpx.Client(
                    proxy="socks5://127.0.0.1:9050", timeout=12.0
                ) as c:
                    r = c.get("https://api.ipify.org?format=json")
                    if r.status_code == 200:
                        self.current_ip = r.json().get("ip", "unknown")
                        self.total_rotations += 1
                        print(f"[✓] IP جديد (Tor): {self.current_ip}")
                        return "socks5://127.0.0.1:9050"
            except Exception:
                pass

            if not self.proxy_list:
                self._scrape_proxies()
            if self.proxy_list:
                p = random.choice(self.proxy_list)
                self.current_ip = p
                self.total_rotations += 1
                print(f"[✓] Proxy: {p}")
                return f"http://{p}"

            print("[!] لا يوجد IP بديل")
            return None

    def _scrape_proxies(self) -> None:
        sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        ]
        found: List[str] = []
        for src in sources:
            try:
                r = httpx.get(src, timeout=15.0)
                if r.status_code != 200:
                    continue
                for line in r.text.strip().splitlines()[:60]:
                    line = line.strip()
                    if line and ":" in line and len(line) < 40:
                        found.append(line)
            except Exception:
                continue
        self.proxy_list = list(dict.fromkeys(found))
        if self.proxy_list:
            print(f"[✓] تم جلب {len(self.proxy_list)} بروكسي")

    def get_proxy(self) -> Optional[str]:
        with self.lock:
            self.request_count += 1
            if self.check_tor():
                return "socks5://127.0.0.1:9050"
            if not self.proxy_list:
                self._scrape_proxies()
            if self.proxy_list:
                return f"http://{random.choice(self.proxy_list)}"
            return None

    def test_connection(self) -> Optional[Dict]:
        proxy = self.get_proxy()
        try:
            kwargs: dict = {"timeout": 12.0}
            if proxy:
                kwargs["proxy"] = proxy
            with httpx.Client(**kwargs) as c:
                r = c.get("https://api.ipify.org?format=json")
                if r.status_code == 200:
                    return {"ip": r.json().get("ip"), "proxy": proxy}
        except Exception:
            return None
        return None
