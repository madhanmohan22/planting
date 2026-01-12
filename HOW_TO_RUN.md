# How to Run LPG Connect System

## Prerequisites
- Python 3.8+ installed
- All dependencies installed (see below)

---

## ⚠️ IMPORTANT: Database Setup

### First Time Setup (ONLY ONCE)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database** (⚠️ THIS WILL DELETE ALL DATA!)
   ```bash
   python init_db.py
   ```
   > **WARNING:** This creates fresh tables but **DELETES ALL existing data**!

3. **Create Sample Users**
   ```bash
   python seed.py
   ```
   > This creates sample users for all roles. **Safe to run multiple times**.

### Every Time You Run the App

**Just run the server** - your data persists in the database!
```bash
cd c:\Users\surya\Downloads\planting
uvicorn app.main:app --reload
```

---

## Default Login Credentials

After running `seed.py`, you'll have these users:

### 1. Admin
- **Username:** `admin`
- **Password:** `adminpassword`
- **Role:** System Administrator

### 2. Plant Manager
- **Username:** `plant1`
- **Password:** `plant123`
- **Role:** Plant Manager (Mumbai Central Plant)

### 3. Super Master
- **Username:** `supermaster1`
- **Password:** `super123`
- **Role:** Super Master (Regional Distribution Hub)

### 4. Distributor
- **Username:** `distributor1`
- **Password:** `dist123`
- **Role:** Distributor (Shah Gas Agency)

---

## Access the Application

Open your browser and go to:
**http://localhost:8000/static/index.html**

---

## Quick Start (Every Time)

1. Open terminal in project folder: `c:\Users\surya\Downloads\planting`
2. Run: `uvicorn app.main:app --reload`
3. Open browser: http://localhost:8000/static/index.html
4. Login with any of the credentials above

---

## Stopping the Server

Press `CTRL+C` in the terminal where uvicorn is running

---

## Troubleshooting

### "Incorrect username or password"
**Solution:** Run `python seed.py` to create the default users

### Database connection error
**Solution:** Check that `DATABASE_URL` in `app/database.py` is correct

### Port already in use
**Solution:** Another instance is running, stop it first or use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Import errors
**Solution:** Make sure you're in the project root directory and dependencies are installed

### Lost all my data!
**Cause:** You ran `python init_db.py` which drops all tables
**Prevention:** Only run `init_db.py` when you want a fresh database. Use `seed.py` to add users.

---

## Data Persistence

✅ **Users persist across server restarts** - You only need to create them once!
⚠️ **Never run `init_db.py` unless you want to reset everything**
