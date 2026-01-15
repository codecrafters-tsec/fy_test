# 🚀 QUICK START GUIDE

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
py init_db.py
py add_sample_data.py
```

### Step 3: Start Servers

**For 150+ Users (Production):**
```bash
start_servers_production.bat
```

**For Testing (Development):**
```bash
start_servers.bat
```

### Step 4: Get Your IP Address
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

### Step 5: Access the System

**Admin:** `http://<YOUR_IP>:5001` (admin / admin123)
**Students:** `http://<YOUR_IP>:5000` (student1 / pass123)

---

## 🎯 Default Credentials

**Admin:** admin / admin123
**Students:** student1-5 / pass123

---

## 🔥 Common Issues

**"Connection refused"** → Check if servers are running
**"Not enough questions"** → Add questions via admin panel
**Students can't connect** → Disable firewall or allow Python
**"Already attempted"** → Delete and recreate student account

---

## 📊 During Exam

1. Keep terminal windows open
2. Monitor admin panel Results tab
3. Keep laptop plugged in

---

## 🔄 Reset for Next Exam

```bash
del exam.db
py init_db.py
py add_sample_data.py
```

**✅ You're ready!**
