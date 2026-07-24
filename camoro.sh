# 🔮 Camoro v5.0 - AI-Powered Security Assessment Framework

**Camoro** is an advanced security assessment tool designed for authorized
penetration testing and security research. It uses AI-powered password
generation to simulate human-like password creation patterns.

## ⚡ Features

- 🔍 **Intelligence Gathering** - Extract comprehensive profile data
- 🧠 **AI Password Generator** - 20,000+ smart passwords mimicking human behavior
- ⚡ **Multi-threaded Attack Engine** - 5+ concurrent threads
- 🔄 **IP Rotation** - Automatic IP change via Tor every N attempts
- 🔑 **Session Manager** - Save and resume sessions
- 📊 **Real-time Progress** - Live stats with speed and ETA
- 🔁 **Resume Support** - Continue from where you left off

## 📦 Installation

### Termux
```bash
pkg update && pkg upgrade -y
pkg install git python python-pip tor -y
git clone https://github.com/YOUR_USERNAME/camoro.git
cd camoro
bash install.sh
