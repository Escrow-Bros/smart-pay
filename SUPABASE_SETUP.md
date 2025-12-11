# Supabase Integration Guide

## Overview
GigSmartPay uses Supabase PostgreSQL for persistent, production-grade database storage. Your data will persist across deployments on Render.

## Quick Setup

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in:
   - Project name: `gigsmartpay` (or your choice)
   - Database password: Generate a strong password (save this!)
   - Region: Choose closest to your users
4. Click "Create new project" (takes ~2 minutes)

### 2. Get Your Connection String

1. In your Supabase project, go to **Settings** (⚙️) → **Database**
2. Scroll to **Connection string** section
3. Select **URI** tab
4. Copy the connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual database password

**⚠️ Important:** If your password contains special characters like `@`, `#`, `%`, encode them:
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`

**Example:**
```bash
# Password: Maverick@9845
# Encoded:  Maverick%409845
DATABASE_URL=postgresql://postgres:Maverick%409845@db.eztwselolejaenphcevb.supabase.co:5432/postgres
```

### 3. Set Environment Variable Locally

Add to your `.env` file in the project root:

```bash
DATABASE_URL=postgresql://postgres:YOUR_ENCODED_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
```

### 4. Initialize Database

```bash
pip install -r requirements.txt
python3 scripts/init_supabase.py
```

This will:
- ✅ Create the `jobs` table
- ✅ Create the `disputes` table
- ✅ Set up all indexes
- ✅ Verify connection works

### 5. Test Locally

Start your backend:

```bash
cd backend
python3 api.py
```

You should see the server start successfully. Create a test job through the web interface to verify everything works.

## Deploy to Render

### 1. Add Environment Variable on Render

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Add a new environment variable:
   - **Key:** `DATABASE_URL`
   - **Value:** Your Supabase connection string (with URL-encoded password)
   ```
   postgresql://postgres:Maverick%409845@db.eztwselolejaenphcevb.supabase.co:5432/postgres
   ```
5. Click **Save Changes**

### 2. Redeploy

Render will automatically redeploy with the new environment variable. Your data will now persist across deployments! 🎉

## How It Works

The application **requires** `DATABASE_URL` to be set. It will not start without it.

- ✅ **Production (Render):** Uses Supabase PostgreSQL via `DATABASE_URL`
- ✅ **Local Development:** Uses Supabase PostgreSQL via `.env` file
- ❌ **No SQLite fallback** - ensures consistent database everywhere

## Troubleshooting

### Connection Errors

If you see connection errors:

1. **Check your password:** Make sure you replaced `[YOUR-PASSWORD]` with actual password
2. **Check IP allowlist:** In Supabase, go to **Settings** → **Database** → **Connection Pooling**
   - Make sure connection pooling is enabled
   - Or disable SSL requirement: Add `?sslmode=require` to connection string
3. **Test connection:**
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect('YOUR_DATABASE_URL'); print('✅ Connected!')"
   ```

### Migration Issues

If migration script fails:

1. Check that SQLite database exists: `ls -la gigshield.db`
2. Check Supabase connection: Test with psycopg2 above
3. Run migration with verbose errors:
   ```bash
   python -u scripts/migrate_to_supabase.py
   ```

### SSL Certificate Errors

If you get SSL errors on Render, modify your connection string:

```
postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres?sslmode=require
```

## Database Schema

Both SQLite and PostgreSQL use the same schema:

### Jobs Table
- `job_id` (INTEGER PRIMARY KEY)
- `client_address`, `worker_address` (TEXT)
- `description`, `location` (TEXT)
- `latitude`, `longitude` (REAL)
- `reference_photos`, `proof_photos` (JSON as TEXT)
- `amount` (REAL)
- `status` (TEXT: OPEN, IN_PROGRESS, SUBMITTED, COMPLETED, DISPUTED)
- `created_at`, `assigned_at`, `completed_at` (TIMESTAMP)
- `tx_hash`, `verification_result` (TEXT)
- `acceptance_criteria`, `verification_plan`, `verification_summary` (JSON as TEXT)

### Disputes Table
- `dispute_id` (SERIAL PRIMARY KEY)
- `job_id` (INTEGER, foreign key)
- `raised_by` (TEXT: system, client, worker)
- `raised_at` (TIMESTAMP)
- `reason` (TEXT)
- `ai_verdict` (JSON as TEXT)
- `evidence_photos` (JSON as TEXT)
- `status` (TEXT: PENDING, RESOLVED)
- `resolved_by`, `resolution`, `resolution_notes` (TEXT)
- `resolved_at` (TIMESTAMP)

## Cost

Supabase Free Tier includes:
- 500 MB database storage
- Unlimited API requests
- 2 GB file storage
- 50,000 monthly active users

Perfect for getting started! Upgrade to Pro ($25/mo) when you scale.

## Support

If you encounter issues:
1. Check Supabase logs: Project → Logs → Database
2. Check application logs: Render → Logs
3. Test connection string locally first
4. Verify all environment variables are set correctly

---

**Next Steps:**
1. ✅ Set up Supabase project
2. ✅ Add DATABASE_URL to .env locally
3. ✅ Test locally
4. ✅ Add DATABASE_URL to Render environment
5. ✅ Deploy and verify data persists
