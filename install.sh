#!/bin/bash

# Camoro v4 - Termux Installer
# Instagram Security Assessment Framework

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     ██████╗ █████╗ ███╗   ███╗ ██████╗ ██████╗  ██████╗ "
echo "║    ██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗"
echo "║    ██║     ███████║██╔████╔██║██║   ██║██████╔╝██║   ██║"
echo "║    ██║     ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║   ██║"
echo "║    ╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║╚██████╔╝"
echo "║     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ "
echo "║                                                      ║"
echo "║   🔥 v4.0 - AI-Powered | IP Rotation | Destroyer     ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[*] جاري تثبيت Camoro v4...${NC}"
sleep 1

# تحديث Termux
echo -e "${CYAN}[1/5] تحديث الحزم...${NC}"
pkg update -y && pkg upgrade -y

# تثبيت الأدوات الأساسية
echo -e "${CYAN}[2/5] تثبيت الأدوات...${NC}"
pkg install -y python python-pip git curl wget openssl tor privoxy net-tools

# تثبيت بايثون المكتبات
echo -e "${CYAN}[3/5] تثبيت مكتبات بايثون...${NC}"
pip install --upgrade pip
pip install httpx[http2] colorama requests[socks]

# إعداد Tor
echo -e "${CYAN}[4/5] إعداد Tor...${NC}"
cat > /data/data/com.termux/files/usr/etc/tor/torrc << 'EOF'
## Tor Configuration for Camoro
SOCKSPort 9050
ControlPort 9051
CookieAuthentication 1
ExitNodes {us},{uk},{ca},{de},{fr},{nl}
StrictNodes 0
EOF

# إعداد Privoxy
echo -e "${CYAN}[5/5] إعداد Privoxy...${NC}"
cat > /data/data/com.termux/files/usr/etc/privoxy/config << 'EOF'
listen-address 127.0.0.1:8118
forward-socks5t / 127.0.0.1:9050 .
EOF

# صلاحيات
chmod +x camoro.sh

echo -e "\n${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ CAMORO v4 INSTALLED!              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "  ${YELLOW}📌 قبل التشغيل لأول مرة:${NC}"
echo -e "  ${CYAN}1.${NC} شغّل Tor:      ${WHITE}tor &${NC}"
echo -e "  ${CYAN}2.${NC} شغّل Privoxy:  ${WHITE}privoxy &${NC}"
echo -e "  ${CYAN}3.${NC} شغّل الأداة:   ${WHITE}./camoro.sh${NC}"
echo -e ""
echo -e "  ${YELLOW}💡 تغيير IP يدوي:${NC}"
echo -e "  ${WHITE}pkill -HUP tor${NC}"
echo -e ""
