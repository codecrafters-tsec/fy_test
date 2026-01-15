# 🎓 LAN-Based MCQ Exam System

A complete exam management system for coding club enrollment, supporting ~50 concurrent students on a local network.

## 📋 Features

### Student Side
- ✅ Secure login (no signup)
- ✅ One attempt per student
- ✅ Randomized questions
- ✅ Time-limited exam with countdown timer
- ✅ Auto-submit on timeout
- ✅ Page refresh protection
- ✅ Score display after submission
- ✅ No correct answers shown

### Admin Side
- ✅ Secure admin panel (separate port)
- ✅ Question management (Add/Edit/Delete)
- ✅ Student management (Create accounts)
- ✅ Exam settings (Duration, question count)
- ✅ Results viewing with rankings
- ✅ CSV export functionality

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite
- **Deployment**: LAN (localhost accessible via IP)

## 📁 Project Structure

```
fyweb/
├── app.py                  # Student portal (Port 5000)
├── admin_app.py            # Admin panel (Port 5001)
├── init_db.py              # Database initialization
├── exam.db                 # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── static/                 # Student frontend
│   ├── login.html
│   ├── instructions.html
│   ├── exam.html
│   └── result.html
└── admin_static/           # Admin frontend
    ├── admin_login.html
    └── dashboard.html
```

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
cd d:\club\fyweb
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_db.py
```

This creates:
- Default admin account: `admin` / `admin123`
- Database tables
- Default exam settings (30 min, 10 questions)

### 3. Start Both Servers

**Terminal 1 - Student Portal:**
```bash
python app.py
```
Runs on: `http://0.0.0.0:5000`

**Terminal 2 - Admin Panel:**
```bash
python admin_app.py
```
Runs on: `http://0.0.0.0:5001`

### 4. Find Your Local IP Address

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

**Linux/Mac:**
```bash
ifconfig
```

### 5. Access URLs

**For Students:**
```
http://<YOUR_IP>:5000
Example: http://192.168.1.100:5000
```

**For Admin:**
```
http://<YOUR_IP>:5001
Example: http://192.168.1.100:5001
```

## 👨‍💼 Admin Usage Guide

### First Time Setup

1. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

2. **Add Questions:**
   - Go to "Questions" tab
   - Click "Add Question"
   - Enter question, 4 options, and correct answer
   - Add at least 10 questions (or match your exam settings)

3. **Create Student Accounts:**
   - Go to "Students" tab
   - Click "Add Student"
   - Create username and password for each student
   - Share credentials with students

4. **Configure Exam Settings:**
   - Go to "Settings" tab
   - Set exam duration (minutes)
   - Set number of questions per exam
   - Click "Save Settings"

### During Exam

- Monitor "Results" tab for real-time submissions
- View rankings automatically

### After Exam

- View complete results with rankings
- Export to CSV for record-keeping

## 👨‍🎓 Student Usage Guide

1. Connect to the same Wi-Fi network as the host laptop
2. Open browser and go to `http://<HOST_IP>:5000`
3. Login with provided credentials
4. Read instructions carefully
5. Click "Start Exam" (timer begins immediately)
6. Answer questions (can navigate freely)
7. Submit before time expires (or auto-submit)
8. View your score

## 🔒 Security Features

- Password hashing (SHA-256)
- Session-based authentication
- Role-based access control
- One attempt enforcement
- Direct URL access prevention
- Admin panel on separate port

## 🗄️ Database Schema

### users
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `role`: 'student' or 'admin'
- `attempted`: 0 or 1 (attempt tracking)

### questions
- `id`: Primary key
- `question`: Question text
- `option_a`, `option_b`, `option_c`, `option_d`: Options
- `correct_answer`: 'A', 'B', 'C', or 'D'

### answers
- `id`: Primary key
- `user_id`: Foreign key to users
- `question_id`: Foreign key to questions
- `selected_answer`: Student's answer

### results
- `id`: Primary key
- `user_id`: Foreign key to users
- `score`: Number of correct answers
- `total_questions`: Total questions in exam
- `submitted_at`: Timestamp

### exam_settings
- `id`: Primary key (always 1)
- `duration_minutes`: Exam duration
- `questions_per_exam`: Number of questions

## 🌐 Network Configuration

### For ~50 Concurrent Users

1. **Use a good Wi-Fi router** (supports 50+ devices)
2. **Host laptop requirements:**
   - Stable power supply
   - Good Wi-Fi connection
   - At least 4GB RAM
   - Windows/Linux/Mac

3. **Firewall settings:**
   - Allow incoming connections on ports 5000 and 5001
   - Windows: `Windows Defender Firewall > Allow an app`

### Testing Connection

From any student device:
```bash
ping <HOST_IP>
```

If ping works, students can access the exam.

## 🐛 Troubleshooting

### Students can't connect
- Check firewall settings
- Verify all devices on same network
- Confirm host IP address is correct
- Ensure both Flask apps are running

### "Not enough questions" error
- Admin must add questions ≥ questions_per_exam setting

### Student already attempted
- This is by design (one attempt only)
- Admin can delete and recreate student account if needed

### Timer not working
- Ensure JavaScript is enabled in browser
- Check browser console for errors

## 📊 Performance Tips

- Close unnecessary applications on host laptop
- Use wired connection for host if possible
- Test with 5-10 students before full deployment
- Keep question bank reasonable (50-100 questions)

## 🔄 Resetting the System

**Reset all student attempts:**
```sql
sqlite3 exam.db "UPDATE users SET attempted = 0 WHERE role = 'student'"
```

**Clear all results:**
```sql
sqlite3 exam.db "DELETE FROM results; DELETE FROM answers;"
```

**Complete reset:**
```bash
del exam.db
python init_db.py
```

## 📝 Important Notes

- ⚠️ Change default admin password after first login
- ⚠️ Backup `exam.db` before making changes
- ⚠️ Test the system with a few students first
- ⚠️ Ensure stable power supply during exam
- ⚠️ Have a backup plan (paper-based) ready

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review browser console for errors
3. Check Flask terminal output for server errors

## 📄 License

Free to use for educational purposes.

---

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

**⚠️ CHANGE THESE IMMEDIATELY AFTER FIRST LOGIN!**
