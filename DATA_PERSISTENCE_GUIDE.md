# Data Persistence Guide - LPG Connect System

## ✅ Good News: Your Data IS Persisting!

Your application uses **CockroachDB cloud database**, which means:
- ✅ Data persists across server restarts
- ✅ Users you create stay in the database
- ✅ All orders, requests, and data remain saved

## Current Database Status

**Users in database right now:**
- ✅ admin (ADMIN) - Active
- ✅ plant1 (PLANT) - Active  
- ✅ supermaster1 (SUPER_MASTER) - Active
- ✅ distributor1 (DISTRIBUTOR) - Active

---

## ⚠️ CRITICAL: Don't Delete Your Data!

### NEVER run these unless you want to DELETE EVERYTHING:
```bash
❌ python init_db.py    # This DELETES ALL TABLES AND DATA!
```

### Safe to run anytime:
```bash
✅ uvicorn app.main:app --reload    # Start server - data persists
✅ python check_db_status.py        # Check what's in database
```

---

## When to Run What

### First Time ONLY (Already Done!):
```bash
pip install -r requirements.txt   # Install dependencies
python init_db.py                 # Create tables (⚠️ DELETES DATA!)
python seed.py                    # Create default users
```

### Every Day Usage:
```bash
# Just start the server!
uvicorn app.main:app --reload
```

Then open: http://localhost:8000/static/index.html

---

## Why You Might Lose Data

**You lose data ONLY if you:**
1. ❌ Run `python init_db.py` again (it drops all tables)
2. ❌ Manually delete data from CockroachDB dashboard
3. ❌ Change the database URL in `app/database.py`

**Data persists when you:**
- ✅ Stop the server (Ctrl+C)
- ✅ Restart your computer
- ✅ Close your terminal
- ✅ Come back tomorrow

---

## How to Check Your Data

**Run this anytime to see what's in your database:**
```bash
python check_db_status.py
```

**Output will show:**
- How many users exist
- List of all usernames and roles
- Warning if you're about to delete data

---

## Adding New Users

### Option 1: Through Admin Dashboard (Recommended)
1. Login as admin at http://localhost:8000/static/index.html
2. Go to "Create Users" section
3. Create Super Masters or Plant Managers
4. **They persist automatically!**

### Option 2: Create Admin script
```bash
python create_admin.py  # Creates additional admin if needed
```

### ❌ DON'T: Run seed.py again
`seed.py` is for initial setup only. Running it again will try to create duplicate users and may cause errors.

---

## Summary

| Command | When to Use | Effect on Data |
|---------|-------------|----------------|
| `init_db.py` | **ONCE** - First setup | ❌ **DELETES ALL DATA** |
| `seed.py` | **ONCE** - After init_db | Creates 4 default users |
| `uvicorn app.main:app --reload` | **EVERY TIME** | ✅ No data loss |
| `check_db_status.py` | Anytime you want | Just reads data |

---

## Your Next Steps

**Starting the app:**
```bash
cd c:\Users\surya\Downloads\planting
uvicorn app.main:app --reload
```

**That's it!** Your data is already in the cloud database and will persist.

**If you ever see "user not found":**
1. Run `python check_db_status.py` to verify users exist
2. If no users exist, then run `python seed.py`
3. If tables don't exist, then run `python init_db.py` then `python seed.py`

---

## Data Location

Your data is stored in:
- **Database**: CockroachDB Cloud
- **URL**: fake-ayeaye-20209.j77.aws-ap-south-1.cockroachlabs.cloud
- **Database Name**: defaultdb
- **Persistence**: Permanent (until you manually delete)
