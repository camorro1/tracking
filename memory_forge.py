#!/usr/bin/env python3
"""
MemoryForge - Runtime Memory Editor
Ethical Hacking & Penetration Testing Tool
Supports: Linux & Android (Termux)
"""

import os
import sys
import signal
import argparse
from modules.process import ProcessManager
from modules.memory_scanner import MemoryScanner
from modules.memory_editor import MemoryEditor

BANNER = """
███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗███████╗
████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔════╝
██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝ █████╗  
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝  ██╔══╝  
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   ███████╗
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
        Runtime Memory Editor - v1.0
   [ Authorized Security Testing Only ]
"""

def print_banner():
    print(BANNER)
    print(f"{'='*60}")
    print(f"  Platform: {sys.platform}")
    print(f"  PID: {os.getpid()}")
    print(f"{'='*60}\n")

def check_root():
    """Check if running as root (required for memory access)"""
    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root!")
        print("   Memory read/write requires root access.")
        print("   Run with: sudo python3 memory_forge.py\n")
        return False
    return True

def list_processes(proc_manager):
    """List all running processes"""
    print("\n[+] Fetching running processes...\n")
    processes = proc_manager.get_all_processes()
    
    print(f"{'PID':<8} {'NAME':<35} {'PACKAGE':<25}")
    print("-" * 70)
    
    for proc in processes[:50]:  # أول 50 عملية
        print(f"{proc['pid']:<8} {proc['name'][:34]:<35} {proc.get('package', '')[:24]:<25}")
    
    print(f"\n... and {len(processes)-50} more processes")
    return processes

def search_menu(scanner):
    """Interactive search menu"""
    results = []
    
    while True:
        print("\n" + "="*50)
        print("  🔍 MEMORY SEARCH MENU")
        print("="*50)
        print("1. New Search (value)")
        print("2. Refine Search (filter results)")
        print("3. Show Results")
        print("4. Edit Value")
        print("5. Back to Main Menu")
        
        choice = input("\n[>] Choose: ").strip()
        
        if choice == "1":
            val = input("[>] Enter value to search (int/float): ").strip()
            try:
                if '.' in val:
                    results = scanner.search_value(float(val), data_type='float')
                else:
                    results = scanner.search_value(int(val), data_type='int')
                print(f"\n[✓] Found {len(results)} matches")
            except Exception as e:
                print(f"[✗] Error: {e}")
        
        elif choice == "2":
            if not results:
                print("[!] No results to refine. Start a new search first.")
                continue
            val = input("[>] Enter new value to filter: ").strip()
            try:
                if '.' in val:
                    results = scanner.refine_search(float(val), data_type='float')
                else:
                    results = scanner.refine_search(int(val), data_type='int')
                print(f"\n[✓] Refined to {len(results)} matches")
            except Exception as e:
                print(f"[✗] Error: {e}")
        
        elif choice == "3":
            if not results:
                print("[!] No results yet.")
                continue
            print(f"\n{'#':<4} {'ADDRESS':<16} {'CURRENT VALUE':<20}")
            print("-" * 42)
            for i, res in enumerate(results[:30]):
                print(f"{i+1:<4} {hex(res['address']):<16} {str(res['value']):<20}")
            if len(results) > 30:
                print(f"... and {len(results)-30} more")
        
        elif choice == "4":
            if not results:
                print("[!] No results to edit.")
                continue
            try:
                idx = int(input("[>] Result index to edit (1-based): ")) - 1
                if idx < 0 or idx >= len(results):
                    print("[!] Invalid index")
                    continue
                new_val = input("[>] New value: ").strip()
                if '.' in new_val:
                    scanner.write_memory(results[idx]['address'], float(new_val), 'float')
                else:
                    scanner.write_memory(results[idx]['address'], int(new_val), 'int')
                print(f"[✓] Value updated!")
            except Exception as e:
                print(f"[✗] Error: {e}")
        
        elif choice == "5":
            break

def edit_direct(editor):
    """Direct memory edit option"""
    print("\n" + "="*50)
    print("  📝 DIRECT MEMORY EDIT")
    print("="*50)
    
    addr_hex = input("[>] Memory address (hex, e.g., 0x7f123456): ").strip()
    try:
        addr = int(addr_hex, 16)
    except ValueError:
        print("[✗] Invalid address format")
        return
    
    val = input("[>] Value to write: ").strip()
    dtype = input("[>] Data type (int/float/double/long): ").strip().lower() or "int"
    
    try:
        if dtype == "int":
            editor.write_value(addr, int(val), 4)
        elif dtype == "float":
            editor.write_value(addr, float(val), 4)
        elif dtype == "double":
            editor.write_value(addr, float(val), 8)
        elif dtype == "long":
            editor.write_value(addr, int(val), 8)
        else:
            print("[✗] Unknown data type")
            return
        print(f"[✓] Written {val} to {hex(addr)}")
    except Exception as e:
        print(f"[✗] Error: {e}")

def hex_dump_menu(scanner):
    """Hex dump memory region"""
    print("\n" + "="*50)
    print("  📊 HEX DUMP")
    print("="*50)
    
    addr_hex = input("[>] Start address (hex): ").strip()
    try:
        addr = int(addr_hex, 16)
    except ValueError:
        print("[✗] Invalid address")
        return
    
    size = input("[>] Size (bytes, default 256): ").strip() or "256"
    size = int(size)
    
    try:
        data = scanner.read_memory_region(addr, size)
        print(f"\n[+] Hex dump of {hex(addr)} ({size} bytes):\n")
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            print(f"{hex(addr+i):<16} {hex_part:<48} {ascii_part}")
    except Exception as e:
        print(f"[✗] Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="MemoryForge - Runtime Memory Editor")
    parser.add_argument("-p", "--pid", type=int, help="Target process PID")
    parser.add_argument("-n", "--name", type=str, help="Target process name")
    parser.add_argument("-s", "--search", type=str, help="Initial value to search")
    parser.add_argument("--list", action="store_true", help="List running processes")
    args = parser.parse_args()
    
    print_banner()
    check_root()
    
    proc_manager = ProcessManager()
    
    # List mode
    if args.list:
        list_processes(proc_manager)
        return
    
    # Select target process
    target_pid = args.pid
    if not target_pid and args.name:
        target_pid = proc_manager.find_pid_by_name(args.name)
        if not target_pid:
            print(f"[✗] No process found with name: {args.name}")
            processes = list_processes(proc_manager)
            return
    
    if not target_pid:
        processes = list_processes(proc_manager)
        try:
            target_pid = int(input("\n[>] Enter target PID: ").strip())
        except ValueError:
            print("[✗] Invalid PID")
            return
    
    # Attach to process
    print(f"\n[+] Attaching to PID {target_pid}...")
    if not proc_manager.attach(target_pid):
        print(f"[✗] Failed to attach to PID {target_pid}")
        sys.exit(1)
    
    proc_info = proc_manager.get_process_info(target_pid)
    print(f"[✓] Attached to: {proc_info.get('name', 'Unknown')} (PID: {target_pid})")
    
    # Initialize scanner and editor
    scanner = MemoryScanner(proc_manager, target_pid)
    editor = MemoryEditor(proc_manager, target_pid)
    
    # Interactive main menu
    while True:
        print("\n" + "="*50)
        print(f"  🎯 MAIN MENU — PID {target_pid}")
        print("="*50)
        print("1. 🔍 Memory Scan (search & edit)")
        print("2. 📝 Direct Memory Edit")
        print("3. 📊 Hex Dump Region")
        print("4. 🔄 Refresh Process Info")
        print("5. 🚪 Exit")
        
        choice = input("\n[>] Choose: ").strip()
        
        if choice == "1":
            search_menu(scanner)
        elif choice == "2":
            edit_direct(editor)
        elif choice == "3":
            hex_dump_menu(scanner)
        elif choice == "4":
            proc_info = proc_manager.get_process_info(target_pid)
            print(f"[✓] Refreshed: {proc_info.get('name', 'Unknown')}")
        elif choice == "5":
            print("\n[+] Detaching from process...")
            proc_manager.detach(target_pid)
            print("[✓] Exiting. Stay ethical! 🔒")
            break
        else:
            print("[!] Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(0)
