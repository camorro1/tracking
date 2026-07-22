#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro - Termux Penetration Testing Framework
Author: Your Name
Version: 1.0
"""

import sys
import os
import signal
from banner import show_banner
from modules.payload import PayloadModule
from modules.scanner import ScannerModule
from modules.exploit import ExploitModule
from modules.session import SessionModule

def signal_handler(sig, frame):
    print("\n[!] Exiting Camorro...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    os.system("clear")
    show_banner()
    
    modules = {
        "1": {"name": "Payload Generator", "module": PayloadModule()},
        "2": {"name": "Network Scanner", "module": ScannerModule()},
        "3": {"name": "Exploitation Engine", "module": ExploitModule()},
        "4": {"name": "Session Manager", "module": SessionModule()},
        "5": {"name": "About & Help", "module": None}
    }
    
    while True:
        print("\n" + "═" * 60)
        print("  MAIN MENU")
        print("═" * 60)
        for key, mod in modules.items():
            print(f"  [{key}] {mod['name']}")
        print("  [0] Exit")
        print("═" * 60)
        
        choice = input("\n  Camorro > ").strip()
        
        if choice == "0":
            print("\n  [!] Shutting down Camorro. Goodbye!\n")
            sys.exit(0)
        elif choice in modules:
            mod = modules[choice]["module"]
            if mod:
                mod.run()
            else:
                show_about()
        else:
            print("  [!] Invalid option, try again.")

def show_about():
    print("""
    ╔══════════════════════════════════════════╗
    ║           CAMORRO v1.0                   ║
    ║  Termux Penetration Testing Framework    ║
    ║  Authorized use only.                    ║
    ╚══════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
