#!/bin/bash

# Camoro - Termux Installation Script
# Instagram Security Assessment Tool

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║         🔮 CAMORO INSTALLER              ║"
echo "║   Instagram Security Assessment Tool      ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running on Termux
if [ -d "/data/data/com.termux/files/usr" ]; then
    echo -e "${GREEN}[✓] Termux detected${NC}"
else
    echo -e "${YELLOW}[!] Not Termux, but continuing...${NC}"
fi

echo -e "${CYAN}[*] Updating packages...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${CYAN}[*] Installing Python and dependencies...${NC}"
pkg install -y python python-pip git curl wget

echo -e "${CYAN}[*] Installing Python libraries...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${CYAN}[*] Generating common passwords list...${NC}"
python modules/utils.py --generate-wordlist

chmod +x camoro.sh

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║     ✅ CAMORO INSTALLED SUCCESSFULLY      ║"
echo "║                                           ║"
echo "║   Run: ./camoro.sh                      ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
