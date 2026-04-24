# 🌾 AgroAI - Smart Crop Recommendation System

Complete full-stack application for intelligent crop recommendations combining machine learning, weather integration, and mobile interface.

## Project Structure

```
agroai/
├── agro-api/              # FastAPI backend
│   ├── app/
│   │   ├── main.py        # FastAPI application + endpoints
│   │   ├── schemas.py     # Pydantic validation models
│   │   ├── model.py       # ML model manager
│   │   ├── services.py    # Business logic
│   │   └── weather.py     # Weather API integration
│   ├── model/
│   │   └── crop_model.pkl # Trained RandomForest model
│   ├── scripts/
│   │   └── train_model.py # Model training script
│   ├── test_main.py       # Pytest test suite (16 tests)
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Docker configuration
│   ├── README.md          # Backend documentation
│   └── TEST_GUIDE.md      # Testing guide
│
└── agro-app/              # React Native mobile app
    ├── App.js             # Navigation root
    ├── app.json           # Expo configuration
    ├── package.json       # JavaScript dependencies
    ├── screens/
    │   ├── HomeScreen.js  # Input form
    │   └── ResultScreen.js # Results display
    ├── components/
    │   ├── AlertBanner.js
    │   ├── InputCard.js
    │   ├── FertilizerCard.js
    │   └── CropResultCard.js
    ├── services/
    │   └── api.js         # API client
    └── constants/
        └── theme.js       # Design system
```

## Quick Start

### Backend Setup

```bash
cd agro-api

# Install dependencies
pip install -r requirements.txt

# Run tests (16 tests, all passing)
pytest test_main.py -v

# Start server
uvicorn app.main:app --reload
# Server: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Mobile App Setup

```bash
cd agro-app

# Install dependencies
npm install

# Start Expo
npx expo start
# Scan QR code with Expo Go app on iOS/Android
```

## API Endpoints

### Health Check
```
GET /
Response: { "status": "ok", "service": "AgroAI API", "model_loaded": true }
```

### Basic Recommendation
```
POST /recommend
Body: {
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "temperature": 28.0,      (optional)
  "humidity": 82.0           (optional)
}
Response: RecommendResponse
```

### Advanced (Weather-Aware)
```
POST /recommend-advanced
Body: {
  "N": 90,
  "P": 42,
  "K": 43,
  "ph": 6.5,
  "latitude": 17.3850,       (required)
  "longitude": 78.4867       (required)
}
Response: RecommendResponse with weather_used flag
```

## Test Results

✅ **16/16 tests passing** (2.88 seconds)

- Health Check: 1 test
- Input Validation: 5 tests
- Weather Integration: 5 tests
- Response Schema: 2 tests
- Edge Cases: 3 tests

```bash
# Run tests
cd agro-api && pytest test_main.py -v
```

## Features

✅ ML-powered crop prediction (22 crops)  
✅ Soil health analysis and scoring  
✅ Smart fertilizer recommendations  
✅ Real-time weather integration  
✅ Location-based lookup  
✅ Input validation (Pydantic)  
✅ Error handling with JSON responses  
✅ Type safety (Python 3.8+)  
✅ Structured logging  
✅ CORS enabled  

## Configuration

### Backend (.env)
```
OPENWEATHER_API_KEY=your_api_key_here
```

### Frontend (api.js)
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

For deployment, update to production URL.

## Deployment

### Docker
```bash
cd agro-api
docker build -t agroai-api .
docker run -p 8000:8000 agroai-api
```

### Cloud (Render.com, Heroku, etc.)
- Push backend to GitHub
- Connect repo to cloud platform
- Set `OPENWEATHER_API_KEY` environment variable
- Deploy

### Mobile App
- Build with EAS: `eas build --platform ios --platform android`
- Submit to App Store and Google Play

## Documentation

- **Backend:** `agro-api/README.md`
- **Testing:** `agro-api/TEST_GUIDE.md`
- **Planning:** `CURSOR_PLAN.md`

## Requirements

- Python 3.8+
- Node.js 16+
- npm or yarn
- iOS/Android emulator or device (for mobile)

## Status

✅ **Production Ready**

- All code tested and validated
- Full type safety
- Comprehensive error handling
- Ready for deployment

## License

MIT
