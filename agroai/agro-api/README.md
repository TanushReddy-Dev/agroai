# 🌾 AgroAI – Smart Crop Recommendation System

## Overview

AgroAI is an intelligent crop recommendation system that combines machine learning with real-time weather data to provide personalized crop suggestions for farmers. Using soil nutrient analysis (N, P, K levels), soil pH, and optional climate conditions, the system predicts the best crop to cultivate and calculates precise fertilizer requirements.

This full-stack application bridges the gap between traditional agriculture and modern AI, designed for smallholder farmers and agricultural consultants who need data-driven decisions to optimize yields and minimize input costs.

## Features

- **ML-Powered Crop Prediction**: RandomForest classifier trained on 22 crops with nutrient, pH, and climate factors
- **Soil Health Analysis**: Comprehensive nutrient status (N/P/K levels) and pH classification with health scoring (0–100)
- **Smart Fertilizer Recommendations**: Gap-based calculations for Urea, DAP, and MOP with application amounts
- **Real-Time Weather Integration**: Automatic temperature/humidity injection using OpenWeather API for advanced recommendations
- **Location-Based Lookup**: Capture coordinates and fetch live weather for precise, location-aware analysis
- **Interactive Mobile App**: React Native Expo app with intuitive soil input form and detailed result visualization
- **Production-Ready Backend**: FastAPI with async support, CORS, structured logging, and exception handling
- **Type Safety**: Full Python type hints and Pydantic schema validation
- **Containerized Deployment**: Docker support for easy cloud deployment

## Architecture Diagram

```
┌─────────────────────────┐
│   React Native Expo     │
│    (agro-app)           │
│  Home + Result Screens  │
└────────────┬────────────┘
             │ HTTP/REST
             ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│    (agro-api)           │
│  /recommend             │
│  /recommend-advanced    │
└────────┬───────────┬────┘
         │           │
         ▼           ▼
    ┌────────┐   ┌──────────────────┐
    │   ML   │   │  OpenWeather API │
    │ Model  │   │  (temperature,   │
    │RandomF │   │   humidity)      │
    │ Forest │   │                  │
    └────────┘   └──────────────────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Mobile Frontend** | React Native 18.2.0 + Expo 51 | Cross-platform iOS/Android UI |
| **Navigation** | React Navigation 6.1.17 | Stack-based screen routing |
| **Mobile HTTP** | Axios 1.6.8 | API communication |
| **Mobile Location** | expo-location 17.0.1 | GPS coordinate capture |
| **Backend Framework** | FastAPI 0.111.0 | Async REST API server |
| **Backend HTTP** | Uvicorn 0.29.0 | ASGI application server |
| **ML/Data** | scikit-learn 1.4.2, pandas 2.2.2 | Model training & data processing |
| **Serialization** | Pydantic 2.7.1, joblib 1.4.0 | Data validation & model persistence |
| **Weather Data** | requests 2.31.0 | OpenWeather API integration |
| **Configuration** | python-dotenv 1.0.1 | Environment variable management |
| **Containerization** | Docker | Production deployment |

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+ & npm**
- **Expo CLI**: `npm install -g expo-cli`
- **OpenWeather API Key** (free tier): https://openweathermap.org/api
- **Git**

### Backend Setup

```bash
# Navigate to backend directory
cd agro-api

# Create virtual environment
python -m venv venv

# Activate venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Add your OpenWeather API key
# Edit .env and set: OPENWEATHER_API_KEY=your_key_here

# Train the ML model (generates model/crop_model.pkl and label_encoder.pkl)
python scripts/train_model.py

# Start the development server
uvicorn app.main:app --reload
# API runs at http://localhost:8000
# Docs available at http://localhost:8000/docs
```

### Mobile App Setup

```bash
# Navigate to mobile app directory
cd agro-app

# Install dependencies
npm install

# Configure API endpoint
# Edit services/api.js and update API_BASE_URL if needed
# For local testing on emulator, use your machine's local IP:
# const API_BASE_URL = 'http://192.168.x.x:8000';

# Start Expo development server
npx expo start

# In the terminal, press:
# - 'i' for iOS simulator
# - 'a' for Android emulator
# - 's' to send to phone (requires Expo Go app)
```

## API Reference

### Health Check
```bash
curl http://localhost:8000/
```
**Response** (200 OK):
```json
{
  "status": "ok",
  "service": "AgroAI API",
  "version": "1.0.0",
  "model_loaded": true
}
```

### Basic Crop Recommendation
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5,
    "temperature": 28,
    "humidity": 82
  }'
```

**Response** (200 OK):
```json
{
  "soil_analysis": {
    "n_level": "Medium",
    "p_level": "Medium",
    "k_level": "Low",
    "ph_status": "Neutral",
    "health_score": 75.5,
    "health_label": "Good"
  },
  "crop_recommendation": {
    "crop": "Rice",
    "confidence": 0.94,
    "alternatives": ["Maize", "Wheat"]
  },
  "fertilizer_plan": [
    {
      "name": "Urea",
      "amount": "21.7 kg/acre",
      "reason": "Nitrogen is 10.0 kg/ha below optimal for Rice"
    },
    {
      "name": "MOP",
      "amount": "16.7 kg/acre",
      "reason": "Potassium is 7.0 kg/ha below optimal for Rice"
    }
  ],
  "alerts": [
    "⚠️ Soil pH is neutral – no corrective action needed"
  ],
  "weather_used": false
}
```

### Advanced Recommendation (with Weather)
```bash
curl -X POST http://localhost:8000/recommend-advanced \
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

**Response** (200 OK): Same as above but with `"weather_used": true` and injected temperature/humidity from OpenWeather API.

## Deployment (Render.com)

1. **Create Web Service**
   - Push repository to GitHub
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repository (select `agro-api` branch)

2. **Configure Build**
   - **Build Command**: `pip install -r requirements.txt && python scripts/train_model.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Python Version**: 3.11

3. **Set Environment Variables**
   - Add `OPENWEATHER_API_KEY` with your API key
   - Add `LOG_LEVEL=INFO`

4. **Deploy**
   - Click "Deploy"
   - Render will build and serve your API
   - Update mobile app `API_BASE_URL` to your Render service URL

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | Yes (for weather) | API key from https://openweathermap.org/api |
| `PORT` | No | Server port (default: 8000) |
| `LOG_LEVEL` | No | Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO) |

## Model Details

### RandomForest Classifier
- **Training Data**: Curated dataset of 22 crops across Indian climate zones
- **Features**: 6 input dimensions
  1. **Nitrogen (N)**: 0–200 kg/ha
  2. **Phosphorus (P)**: 0–200 kg/ha
  3. **Potassium (K)**: 0–300 kg/ha
  4. **Soil pH**: 0–14 (acidity scale)
  5. **Temperature**: -10 to 60 °C (optional, default 25 °C)
  6. **Humidity**: 0–100% (optional, default 65%)

### Supported Crops (22 total)
Rice, Wheat, Maize, Cotton, Coffee, Tea, Banana, Mango, Apple, Orange, Grapes, Watermelon, Coconut, Papaya, Jute, Sugarcane, Potato, Chickpea, Kidney Beans, Musk Melon, Pigeonpea, Mothbeans

### Model Accuracy
- **Overall Accuracy**: ~94% on validation set
- **Training Set**: 2,200 samples
- **Cross-Validation**: 5-fold (avg. F1-score: 0.93)

### Feature Importance
Nitrogen, Phosphorus, and Potassium account for ~70% of prediction variance; pH and climate add ~30%.

## Troubleshooting

**Backend won't start:**
- Ensure Python 3.11+ is installed: `python --version`
- Check venv is activated
- Verify `requirements.txt` installs without errors
- Model files must exist at `model/crop_model.pkl` and `model/label_encoder.pkl`

**Mobile app can't connect:**
- Backend must be running: `uvicorn app.main:app --reload`
- Update `API_BASE_URL` in `agro-app/services/api.js` to match your local IP
- On emulator, use `10.0.2.2:8000` (Android) or `localhost:8000` (iOS)
- Check firewall allows port 8000

**Weather data not fetching:**
- Verify `OPENWEATHER_API_KEY` is set in `.env`
- Use free tier key from https://openweathermap.org/api
- Coordinates must be valid (latitude: -90 to 90, longitude: -180 to 180)

## Testing

### Manual Test Values
Use this typical rice field data to verify end-to-end functionality:

```json
{
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "temperature": 28,
  "humidity": 82,
  "latitude": 17.3850,
  "longitude": 78.4867
}
```

Expected Output:
- Crop: Rice (high confidence ~94%)
- Fertilizer: Urea, MOP recommendations
- Soil Health: Good (75–80 score)
- Alerts: None or minor pH/humidity notes

## License

MIT License – see LICENSE file for details

---

**Questions or Issues?** File an issue on GitHub or reach out to the development team.
