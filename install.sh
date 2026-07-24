#!/bin/bash

# Camoro - Installer for Termux

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║         🔮 CAMORO INSTALLER v2           ║"
echo "║     Instagram Security Assessment Tool    ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# تحديث الحزم
echo -e "${YELLOW}[*] جاري تحديث الحزم...${NC}"
pkg update -y && pkg upgrade -y

# تثبيت Python والمكتبات
echo -e "${YELLOW}[*] جاري تثبيت Python...${NC}"
pkg install -y python python-pip git curl wget openssl

# ترقية pip
echo -e "${YELLOW}[*] جاري ترقية pip...${NC}"
pip install --upgrade pip

# تثبيت المكتبات المطلوبة
echo -e "${YELLOW}[*] جاري تثبيت المكتبات...${NC}"
pip install httpx[http2] colorama

# صلاحيات التنفيذ
chmod +x camoro.sh

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════╗"
echo "║     ✅ CAMORO INSTALLED SUCCESSFULLY      ║"
echo "║                                           ║"
echo "║   للتشغيل: ./camoro.sh                  ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
