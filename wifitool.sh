#!/bin/bash
# WiFi Pentest Toolkit v1.0 - Main Launcher
# Authorized security testing only

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

mkdir -p capture logs portals modules

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$BASE_DIR/logs/session.log"
}

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}[!] Root required. Use: sudo bash wifitool.sh  (or tsu on Termux)${NC}"
        exit 1
    fi
}

banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
 __        ___ _____ _   ____            _            _
 \ \      / (_)  ___(_) |  _ \ ___ _ __ | |_ ___  ___| |_
  \ \ /\ / /| | |_  | | | |_) / _ \ '_ \| __/ _ \/ __| __|
   \ V  V / | |  _| | | |  __/  __/ | | | ||  __/\__ \ |_
    \_/\_/  |_|_|   |_| |_|   \___|_| |_|\__\___||___/\__|
EOF
    echo -e "${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}     WiFi Pentest Toolkit ${GREEN}v1.0${NC}               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}     Authorized Security Testing Only          ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
}

list_ifaces() {
    echo -e "${YELLOW}Available interfaces:${NC}"
    if command -v iw >/dev/null 2>&1; then
        iw dev 2>/dev/null | awk '/Interface/{print "  - "$2}'
    fi
    ifconfig -a 2>/dev/null | awk '/^[a-zA-Z0-9]/ {print "  - "$1}' | tr -d ':'
    ip -o link show 2>/dev/null | awk -F': ' '{print "  - "$2}'
    echo ""
}

menu() {
    banner
    echo -e "${YELLOW}Select module:${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} Evil Twin AP + Captive Portal"
    echo -e "  ${GREEN}2)${NC} Deauth Attack (disconnect clients)"
    echo -e "  ${GREEN}3)${NC} Evil Twin + Deauth (combo)"
    echo -e "  ${GREEN}4)${NC} WPA Handshake Capture"
    echo -e "  ${GREEN}5)${NC} Scan nearby networks"
    echo -e "  ${GREEN}6)${NC} View captured credentials"
    echo -e "  ${GREEN}7)${NC} Cleanup / restore network"
    echo -e "  ${RED}0)${NC} Exit"
    echo ""
    read -rp "$(echo -e ${CYAN}'> '${NC})" choice

    case "$choice" in
        1)
            require_root
            log_msg "Started Evil Twin module"
            bash "$BASE_DIR/modules/evil-twin.sh"
            ;;
        2)
            require_root
            log_msg "Started Deauth module"
            bash "$BASE_DIR/modules/deauth.sh"
            ;;
        3)
            require_root
            log_msg "Started Combo EvilTwin+Deauth"
            bash "$BASE_DIR/modules/evil-twin.sh" --with-deauth
            ;;
        4)
            require_root
            log_msg "Started Handshake capture"
            bash "$BASE_DIR/modules/handshake.sh"
            ;;
        5)
            require_root
            log_msg "Started network scan"
            scan_networks
            ;;
        6)
            view_captures
            ;;
        7)
            require_root
            cleanup_all
            ;;
        0)
            echo -e "${GREEN}Bye.${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            sleep 1
            ;;
    esac
}

scan_networks() {
    list_ifaces
    read -rp "Interface (e.g. wlan0): " IFACE
    [ -z "$IFACE" ] && echo -e "${RED}No interface${NC}" && sleep 2 && return

    echo -e "${GREEN}[+] Enabling monitor mode...${NC}"
    airmon-ng check kill >/dev/null 2>&1
    airmon-ng start "$IFACE" >/dev/null 2>&1
    MON="${IFACE}mon"
    if ! iwconfig "$MON" >/dev/null 2>&1; then
        MON="$IFACE"
    fi

    OUT="$BASE_DIR/capture/scan_$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}Scanning 20s... Ctrl+C to stop earlier${NC}"
    timeout 20 airodump-ng --output-format csv -w "$OUT" "$MON" || \
        airodump-ng --output-format csv -w "$OUT" "$MON" &
    PID=$!
    sleep 20
    kill "$PID" 2>/dev/null || true

    CSV=$(ls -1 "${OUT}"*.csv 2>/dev/null | head -n1)
    if [ -n "$CSV" ]; then
        echo -e "\n${GREEN}=== Nearby APs ===${NC}"
        awk -F',' '
          BEGIN{printf "%-18s %-6s %-4s %-20s\n","BSSID","CH","PWR","ESSID"}
          /Station MAC/{exit}
          NR>2 && $1 ~ /([0-9A-Fa-f]{2}:){5}/ {
            bssid=$1; ch=$4; pwr=$9; essid=$14;
            gsub(/^[ \t]+|[ \t]+$/,"",bssid)
            gsub(/^[ \t]+|[ \t]+$/,"",ch)
            gsub(/^[ \t]+|[ \t]+$/,"",pwr)
            gsub(/^[ \t]+|[ \t]+$/,"",essid)
            if (length(bssid)>0) printf "%-18s %-6s %-4s %-20s\n", bssid, ch, pwr, essid
          }' "$CSV"
        echo -e "\n${BLUE}Saved: $CSV${NC}"
    else
        echo -e "${YELLOW}No CSV produced. Open airodump interactively:${NC}"
        airodump-ng "$MON"
    fi

    echo ""
    read -rp "Press Enter to continue..."
    airmon-ng stop "$MON" >/dev/null 2>&1 || true
}

view_captures() {
    banner
    echo -e "${YELLOW}Captured credentials:${NC}\n"
    if [ -s "$BASE_DIR/logs/captured_passwords.log" ]; then
        cat "$BASE_DIR/logs/captured_passwords.log"
    else
        echo -e "${RED}No captures yet.${NC}"
    fi
    echo ""
    echo -e "${YELLOW}Handshake/capture files:${NC}"
    ls -lah "$BASE_DIR/capture" 2>/dev/null || true
    echo ""
    read -rp "Press Enter..."
}

cleanup_all() {
    echo -e "${YELLOW}[*] Cleaning up...${NC}"
    killall hostapd dnsmasq python3 php aireplay-ng airodump-ng 2>/dev/null || true
    # restore NetworkManager if present
    if command -v systemctl >/dev/null 2>&1; then
        systemctl start NetworkManager 2>/dev/null || true
        systemctl start wpa_supplicant 2>/dev/null || true
        systemctl start networking 2>/dev/null || true
    fi
    # stop monitor interfaces
    for i in $(iw dev 2>/dev/null | awk '/Interface/{print $2}'); do
        airmon-ng stop "$i" >/dev/null 2>&1 || true
    done
    ip link set wlan0 down 2>/dev/null || true
    ip link set wlan0 up 2>/dev/null || true
    rm -f /tmp/hostapd.conf /tmp/dnsmasq.conf /tmp/wifitool_* 2>/dev/null || true
    echo -e "${GREEN}[✓] Cleanup done${NC}"
    sleep 2
}

# trap cleanup on exit of combo modes? leave to modules
while true; do
    menu
done
