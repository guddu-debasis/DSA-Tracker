# Deploying DSA Tracker

Stack: MongoDB Atlas (DB) → Render (FastAPI backend) → Netlify (React frontend).

## 1. Push this repo to GitHub
```bash
cd "E:\DSA Tracker"
git init
git add .
git commit -m "DSA Tracker: initial commit"
```
Create a new (private is fine) repo on GitHub, then:
```bash
git remote add origin https://github.com/<you>/dsa-tracker.git
git branch -M main
git push -u origin main
```

## 2. MongoDB Atlas
1. https://cloud.mongodb.com → create a free (M0) cluster.
2. Database Access → add a DB user with a password (save it).
3. Network Access → add IP `0.0.0.0/0` (allow from anywhere — Render's IPs aren't static on the free tier).
4. Connect → Drivers → copy the connection string. It looks like:
   `mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   Add your DB name before the `?`: `.../dsa_tracker?retryWrites=true...`
   That full string is your `MONGO_URI`.

## 3. Backend on Render
1. https://dashboard.render.com → New → Blueprint → connect your GitHub repo.
   Render will read `render.yaml` at the repo root and detect the `dsa-tracker-api` service
   (root dir `backend`, build/start commands already set).
2. It'll prompt for the env vars marked `sync: false`:
   - `MONGO_URI` → the Atlas connection string from step 2
   - `JWT_SECRET` → any long random string (e.g. generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `CORS_ORIGINS` → leave as `http://localhost:5173` for now, you'll update it after Netlify is live
3. Deploy. Once live, note your backend URL, e.g. `https://dsa-tracker-api.onrender.com`.
4. Check `https://dsa-tracker-api.onrender.com/health` returns `{"status": "ok"}`.

   Note: Render's free tier spins down after 15 min idle — the first request after
   a sleep takes ~30-50s to wake up. Normal for free tier, not a bug.

## 4. Seed the production database
Run the seed script locally, pointed at Atlas instead of localhost:
```bash
cd backend
# temporarily set MONGO_URI to your Atlas string, e.g. in .env or:
set MONGO_URI=mongodb+srv://...        # Windows PowerShell: $env:MONGO_URI="..."
python seed.py
```

## 5. Frontend on Netlify
1. https://app.netlify.com → Add new site → Import from GitHub → pick this repo.
2. Base directory: `frontend`
   Build command / publish dir are already set via `frontend/netlify.toml`
   (`npm run build`, `dist`).
3. Site settings → Environment variables → add:
   - `VITE_API_URL` = `https://dsa-tracker-api.onrender.com` (your Render URL from step 3)
4. Deploy. Note your Netlify URL, e.g. `https://dsa-tracker.netlify.app`.

## 6. Connect the two: update CORS
Go back to Render → your service → Environment → update:
- `CORS_ORIGINS` = `https://dsa-tracker.netlify.app`
  (comma-separate multiple origins if you also want localhost during dev, e.g.
  `https://dsa-tracker.netlify.app,http://localhost:5173`)

Redeploy the backend for the change to take effect. Then reload the Netlify site —
signup/login should now work end to end.

## Troubleshooting
- **CORS error in browser console** → `CORS_ORIGINS` on Render doesn't match your Netlify URL exactly (check for trailing slash / http vs https).
- **Network error / requests hang** → Render free instance is asleep, first request is just slow — wait ~40s and retry, or upgrade off the free tier for always-on.
- **401 on every request** → `VITE_API_URL` on Netlify doesn't point at the right Render URL, or you're mixing prod/local JWTs (log out and back in after switching environments).
- **Empty questions list** → seed script hasn't been run against the Atlas DB (step 4).
