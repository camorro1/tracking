#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

echo "[*] Installing Camoro v5..."
pkg update -y || true
pkg install -y python git curl tor 2>/dev/null || true
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p modules results sessions
touch modules/__init__.py
chmod +x camoro.sh camoro.py install.sh 2>/dev/null || true

# rename typo if exists
if [ -f modules/proxy_manger.py ] && [ ! -f modules/proxy_manager.py ]; then
  mv modules/proxy_manger.py modules/proxy_manager.py
fi

echo "[✓] CAMORO v5.0 INSTALLED!"
echo "Run: python camoro.py"
