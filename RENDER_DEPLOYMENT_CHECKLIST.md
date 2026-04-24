# Render Deployment Checklist

## ✅ Pre-Deployment Setup (Complete)

- [x] Git repository initialized
- [x] `.gitignore` configured (`.env` excluded)
- [x] `.env.example` template ready
- [x] Dockerfile configured
- [x] `requirements.txt` ready
- [x] Model training script ready
- [x] CORS enabled in FastAPI
- [x] Security: No secrets committed

## 🚀 Render Deployment Steps

### Step 1: Push to GitHub

```bash
cd C:\Users\Tanus\Projects\Rishik

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/agroai.git

# Set main branch
git branch -M main

# Push code
git push -u origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (allows easy repo connection)
3. Go to Dashboard

### Step 3: Create New Web Service

1. Click **New +** button
2. Select **Web Service**
3. Click **Connect GitHub account** (if not connected)
4. Search for `agroai` repository
5. Select it and click **Connect**

### Step 4: Configure Service Settings

**Basic Configuration:**

| Field | Value |
|-------|-------|
| **Name** | `agroai-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r agroai/agro-api/requirements.txt && python agroai/agro-api/scripts/train_model.py` |
| **Start Command** | `cd agroai/agro-api && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Python Version** | `3.11` |

### Step 5: Add Environment Variables

In Render dashboard → **Environment** tab:

```
OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
LOG_LEVEL=INFO
```

**To get OpenWeather API Key:**
1. Go to https://openweathermap.org/api
2. Sign up (free tier available)
3. Create API key in dashboard
4. Copy and paste here

### Step 6: Deploy

1. Click **Deploy** button
2. Wait for build to complete (~3-5 minutes)
3. Check logs for any errors
4. Once deployed, you'll see a URL like: `https://agroai-api.onrender.com`

### Step 7: Test Deployment

```bash
# Health check
curl https://agroai-api.onrender.com/

# Expected response:
# {"status":"ok","service":"AgroAI API","version":"1.0.0","model_loaded":true}

# Test recommendation endpoint
curl -X POST https://agroai-api.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5
  }'
```

### Step 8: Update Mobile App

Edit `agroai/agro-app/services/api.js`:

```javascript
// OLD:
// const API_BASE_URL = 'http://10.60.183.133:8000';

// NEW:
const API_BASE_URL = 'https://agroai-api.onrender.com';
```

Commit and push:

```bash
git add agroai/agro-app/services/api.js
git commit -m "Config: Update API endpoint to Render production URL"
git push origin main
```

## 📊 Render Service Details

**Free Tier Limits:**
- 750 free dyno hours/month
- Can run ONE service 24/7
- Auto-sleeps after 15 min inactivity (paid plans don't)
- Shared CPU

**For Production:**
- Upgrade to **Hobby** ($7/month) or **Standard** ($12/month)
- No auto-sleep, guaranteed uptime

## 🔄 Auto-Deploy

After first deployment, Render auto-deploys on every push to `main`:

1. Make code changes locally
2. Commit: `git commit -m "message"`
3. Push: `git push origin main`
4. Render automatically rebuilds (~2-5 min)
5. New version goes live

## ⚠️ Troubleshooting

### Build Fails

**Check logs:**
- Click service in Render dashboard
- Go to **Logs** tab
- Look for error messages

**Common issues:**
- `ModuleNotFoundError`: Missing package in `requirements.txt`
- `Model not found`: Training script didn't run
- `OPENWEATHER_API_KEY not set`: Add to Environment variables

### Service Won't Start

```
Uvicorn needs --host 0.0.0.0 to bind to all interfaces
Port must be set to $PORT (Render variable)
```

Current Start Command is correct:
```
cd agroai/agro-api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Mobile App Can't Connect

1. Verify Render URL is working: `curl https://agroai-api.onrender.com/`
2. Check `API_BASE_URL` in `services/api.js`
3. Rebuild mobile app after changing URL

## ✅ Verification Checklist

After deployment:

- [ ] Service is running on Render dashboard
- [ ] Health endpoint returns: `{"status":"ok",...}`
- [ ] `/docs` shows Swagger UI
- [ ] `/recommend` endpoint works
- [ ] `/recommend-advanced` endpoint works
- [ ] Mobile app successfully connects and makes requests
- [ ] Weather data fetches correctly

## 📞 Support Links

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
- Uvicorn Docs: https://www.uvicorn.org/
- OpenWeather API: https://openweathermap.org/api
