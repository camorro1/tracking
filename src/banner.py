#!/usr/bin/env python3
from colorama import Fore, Back, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import os

init(autoreset=True)

R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
C = Fore.CYAN
M = Fore.MAGENTA
W = Fore.WHITE
B = Fore.BLUE
RS = Style.RESET_ALL

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    clear_screen()
    
    console = Console()
    
    banner_text = f"""
{R}██████╗ █████╗ ███╗   ███╗ █████╗ ██████╗  ██████╗ 
{R}██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗██╔═══██╗
{R}██║     ███████║██╔████╔██║███████║██████╔╝██║   ██║
{R}██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║
{R}╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝
{R} ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
{C}╔══════════════════════════════════════════════════╗
{C}║     {W}INSTAGRAM SECURITY ASSESSMENT FRAMEWORK     {C}║
{C}║     {Y}AI-Powered  |  Multi-Vector  |  Stealth     {C}║
{C}║     {M}Authorized Pentesting Tool Only             {C}║
{C}╚══════════════════════════════════════════════════╝
{RS}"""
    
    print(banner_text)
    
    version_text = Text("v3.0.0 - Advanced Edition", style="bold cyan")
    console.print(Panel(version_text, border_style="red"))

def print_step(step_num, total, label, status="progress"):
    icons = {"progress": "🔄", "done": "✅", "error": "❌", "wait": "⏳"}
    icon = icons.get(status, "•")
    
    if status == "done":
        print(f"\n{G}{icon} [{step_num}/{total}] {label}{RS}")
    elif status == "error":
        print(f"\n{R}{icon} [{step_num}/{total}] {label}{RS}")
    else:
        print(f"\n{C}{icon} [{step_num}/{total}] {label}{RS}")
