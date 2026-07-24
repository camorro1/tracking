# 🔮 Camoro - Instagram Security Assessment Framework

**Camoro** is an advanced Instagram security testing tool with AI-powered password generation. Designed for authorized security professionals to assess account strength.

## ⚡ Features

- 🔍 **Intelligence Gathering** - Extract public profile data
- 🧠 **AI Password Generator** - ~18,000 smart passwords from gathered intel
- ⚡ **Password Testing Engine** - Tests passwords against Instagram auth
- 🔄 **Full Attack Mode** - Automated info gathering → generation → testing
- 📊 **Real-time Progress** - Live stats, speed, ETA display

## 📦 Installation (Termux)

```bash
pkg update && pkg upgrade -y
pkg install git python python-pip -y
git clone https://github.com/YOUR_USERNAME/camoro.git
cd camoro
pip install -r requirements.txt
chmod +x camoro.sh install.sh
./install.sh    # Auto-install dependencies
./camoro.sh     # Launch the tool
