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

---

## 🚀 Deploying to Render (Free Tier)

Since you are using the **Free Tier**, follow these specific steps to get your app live:

### Step 1: Create the Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository: `https://github.com/madhanmohan22/planting.git`
3. **Settings:**
   - **Name:** `planting-app`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

### Step 2: Add Environment Variables
Click the **Advanced** button or go to the **Environment** tab and add these:

| Key | Value |
|--|--|
| `DATABASE_URL` | *Your CockroachDB Connection String* |
| `PYTHON_VERSION` | `3.10.0` (or leave blank) |

### Step 3: Deployment & Usage
1. Click **Create Web Service**.
2. **First Load:** The first time you open the URL, it might take 1-2 minutes to "wake up" the server. This is normal for Render's free tier.
3. **URL:** Your app will be at `https://your-app-name.onrender.com/static/index.html`.

### ⚠️ Free Tier Limitations:
- **Spin Down:** If no one uses the site for 15 minutes, Render puts it to "sleep". The next person to visit will wait about 30 seconds for it to start.
- **Database:** Since we use CockroachDB, your data will NOT be deleted even if Render sleeps!

---

## Data Persistence

✅ **Users persist across server restarts** - You only need to create them once!
⚠️ **Never run `init_db.py` locally unless you want to reset everything.** (On Render, it runs once per deployment to ensure tables exist).
