# AgroAI Deployment Guide

## 🔒 Security Checklist

- ✅ No real API keys committed to repository
- ✅ `.env` file is gitignored (only `.env.example` in repo)
- ✅ Code reads secrets from environment variables using `os.getenv()`
- ✅ CORS enabled for development (`allow_origins=["*"]`)
- ✅ Production-ready error handling and logging

## 📋 Pre-Deployment Setup

### 1. Local Backend Configuration

```bash
cd agroai/agro-api

# Create .env from template
cp .env.example .env

# Edit .env with your API key
# OPENWEATHER_API_KEY=your_actual_key_here
```

### 2. Verify Backend Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Train ML model (one-time)
python scripts/train_model.py

# Start server on network interface
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test: http://localhost:8000/docs (Swagger UI)
# Health check: curl http://localhost:8000/
```

### 3. Docker Build & Run (Local Testing)

```bash
cd agroai/agro-api

# Build image
docker build -t agroai-api .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  --name agroai-api \
  agroai-api

# Stop container
docker stop agroai-api
```

## 🚀 Deploy to Render.com

### Step 1: Push to GitHub

```bash
# From project root
git remote add origin https://github.com/YOUR_USERNAME/agroai.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Select the repository

### Step 3: Configure Service

| Setting | Value |
|---------|-------|
| **Name** | `agroai-api` |
| **Runtime** | Python 3.11 |
| **Build Command** | `pip install -r agroai/agro-api/requirements.txt && python agroai/agro-api/scripts/train_model.py` |
| **Start Command** | `cd agroai/agro-api && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Root Directory** | Leave empty (uses repo root) |

### Step 4: Add Environment Variables

In Render dashboard → **Environment** tab:

```
OPENWEATHER_API_KEY=your_actual_api_key_here
PORT=10000
LOG_LEVEL=INFO
```

### Step 5: Deploy

1. Click **Deploy**
2. Render builds and starts the service
3. Copy the service URL (e.g., `https://agroai-api.onrender.com`)

### Step 6: Update Mobile App

Edit `agroai/agro-app/services/api.js`:

```javascript
const API_BASE_URL = 'https://agroai-api.onrender.com';  // Replace with your Render URL
```

## 📱 Mobile App Deployment

### Local Testing

```bash
cd agroai/agro-app

# Install dependencies
npm install

# Start Expo
npx expo start

# Press 'a' for Android emulator or 's' for phone (with Expo Go)
```

### Production Deployment

For iOS: Use Expo EAS (paid) or Xcode
For Android: Use Expo EAS (paid) or Android Studio

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure project
eas build --platform android

# Follow prompts for building APK
```

## 🧪 Testing Endpoints

### Health Check

```bash
curl https://agroai-api.onrender.com/
```

### Basic Recommendation

```bash
curl -X POST https://agroai-api.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5
  }'
```

### Advanced with Weather

```bash
curl -X POST https://agroai-api.onrender.com/recommend-advanced \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5,
    "latitude": 17.3850,
    "longitude": 78.4867
  }'
```

## 🔍 Troubleshooting

### Backend Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Ensure all packages in `requirements.txt` are installed |
| `Model not found` | Run `python scripts/train_model.py` to generate `model/crop_model.pkl` |
| `OPENWEATHER_API_KEY not set` | Add to `.env` or Render environment variables |
| `Connection refused` | Check backend is running on `0.0.0.0:8000` |

### Mobile Issues

| Problem | Solution |
|---------|----------|
| `Network Error` | Update `API_BASE_URL` to correct server IP/URL |
| `CORS error` | Backend CORS is enabled by default |
| `Timeout` | Check backend is responding: `curl http://IP:8000/` |

## 📦 Render Pricing

- **Free tier**: 750 hours/month (1 service can run 24/7)
- **Hobby**: $7/month per service
- **Standard**: $12/month per service

For production, recommend **Standard** tier for reliability.

## 🔄 Continuous Deployment

Render auto-deploys on every push to `main`:

1. Push to GitHub: `git push origin main`
2. Render webhook triggers
3. Service rebuilds and redeploys automatically
4. Takes ~2-5 minutes

To disable auto-deploy, go to Settings → **Auto-Deploy** → Off

## 📞 Support

- Backend docs: `https://agroai-api.onrender.com/docs`
- OpenWeather API: https://openweathermap.org/api
- Render docs: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com/
