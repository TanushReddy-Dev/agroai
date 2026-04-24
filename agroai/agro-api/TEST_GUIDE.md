# AgroAI Backend Test Suite

**File:** `agro-api/test_main.py`  
**Framework:** pytest  
**Coverage:** 16 test functions across 5 test classes

---

## Test Classes & Functions

### 1. TestHealthEndpoint (1 test)
Tests the health check endpoint.

- ✅ `test_health_returns_ok` - GET / returns `status="ok"`

### 2. TestRecommendEndpoint (5 tests)
Tests the basic recommendation endpoint with validation.

- ✅ `test_recommend_valid_payload` - Valid input returns 200 with all schema fields
- ✅ `test_recommend_missing_required_field` - Missing "ph" returns 422
- ✅ `test_recommend_invalid_field_type` - String instead of float returns 422
- ✅ `test_recommend_field_out_of_range` - N=250 (max 200) returns 422
- ✅ `test_recommend_ph_out_of_range` - pH=15 (max 14) returns 422

### 3. TestAdvancedRecommendEndpoint (5 tests)
Tests the weather-aware recommendation endpoint and fallback behavior.

- ✅ `test_advanced_requires_coordinates` - Missing lat/lon returns 422
- ✅ `test_advanced_with_weather_api_success` - With valid weather returns `weather_used=true`
- ✅ `test_advanced_weather_fallback_no_api_key` - No API key → `weather_used=false`
- ✅ `test_advanced_weather_api_failure_fallback` - API timeout → `weather_used=false` + warning alert
- ✅ `test_advanced_weather_network_error` - Network error → graceful fallback with 200 response

### 4. TestResponseSchema (2 tests)
Tests response structure and field validation.

- ✅ `test_recommend_response_structure` - All required fields present and correct types
- ✅ `test_fertilizer_recommendation_fields` - FertilizerRecommendation items have name/amount/reason

### 5. TestEdgeCases (3 tests)
Tests boundary conditions.

- ✅ `test_recommend_minimum_values` - All fields at 0 returns 200
- ✅ `test_recommend_maximum_values` - All fields at max returns 200
- ✅ `test_recommend_optional_fields` - Optional temp/humidity handled correctly

---

## Fixtures

### `client`
FastAPI TestClient for making HTTP requests to the app.

```python
@pytest.fixture
def client():
    return TestClient(app)
```

### `mock_model_manager`
Mocks the ML model with standard prediction (Rice, 0.87 confidence).

```python
@pytest.fixture
def mock_model_manager():
    with patch("app.main.model_manager") as mock:
        mock.is_loaded.return_value = True
        mock.predict.return_value = {
            "crop": "Rice",
            "confidence": 0.87,
            "alternatives": ["Wheat", "Maize", "Sugarcane"],
        }
        yield mock
```

### `valid_soil_input`
Standard soil data for basic recommendations.

```python
{
    "N": 90,
    "P": 42,
    "K": 43,
    "ph": 6.5,
}
```

### `valid_soil_input_advanced`
Soil data with weather coordinates for advanced recommendations.

```python
{
    "N": 90, "P": 42, "K": 43, "ph": 6.5,
    "temperature": 28, "humidity": 82,
    "latitude": 17.3850, "longitude": 78.4867,
}
```

---

## Running Tests

### Prerequisites
```bash
cd agro-api
pip install pytest
# (FastAPI and other dependencies should already be in requirements.txt)
```

### Run All Tests
```bash
pytest test_main.py -v
```

### Run Specific Test Class
```bash
pytest test_main.py::TestRecommendEndpoint -v
```

### Run Specific Test
```bash
pytest test_main.py::TestAdvancedRecommendEndpoint::test_advanced_weather_api_failure_fallback -v
```

### Run with Coverage
```bash
pip install pytest-cov
pytest test_main.py --cov=app --cov-report=html
```

### Run in Watch Mode
```bash
pip install pytest-watch
ptw test_main.py
```

---

## Test Coverage

### Endpoints Tested

| Endpoint | Tests | Coverage |
|----------|-------|----------|
| GET / | 1 | Health check response |
| POST /recommend | 5 | Valid input, validation, range checks |
| POST /recommend-advanced | 5 | Coordinates, weather success, fallback scenarios |
| Response Schema | 2 | Structure, field types |
| Edge Cases | 3 | Boundary values |

### Scenarios Covered

✅ **Happy Path:** Valid input → 200 with correct response  
✅ **Validation:** Missing/invalid fields → 422  
✅ **Range Checks:** Values out of bounds → 422  
✅ **Weather Success:** API available and working → weather_used=true  
✅ **Weather Fallback (No Key):** API key not set → weather_used=false  
✅ **Weather Fallback (API Error):** API fails → graceful fallback + alert  
✅ **Weather Fallback (Network):** Network error → graceful fallback  
✅ **Edge Cases:** Min/max values, optional fields  

---

## Mocking Strategy

### Model Manager Mock
```python
with patch("app.main.model_manager") as mock:
    mock.is_loaded.return_value = True
    mock.predict.return_value = {...}
```

Always returns:
- Crop: "Rice"
- Confidence: 0.87
- Alternatives: ["Wheat", "Maize", "Sugarcane"]

### Weather API Mock
```python
with patch("app.main.is_weather_available", return_value=True):
    with patch("app.main.fetch_weather", return_value={...}):
        # Test code
```

Simulates both success and failure scenarios:
- Success: Returns valid weather data
- No API Key: `is_weather_available()` returns False
- API Failure: `fetch_weather()` raises `WeatherAPIError`
- Network Error: `fetch_weather()` raises exception

---

## Expected Test Output

```
test_main.py::TestHealthEndpoint::test_health_returns_ok PASSED
test_main.py::TestRecommendEndpoint::test_recommend_valid_payload PASSED
test_main.py::TestRecommendEndpoint::test_recommend_missing_required_field PASSED
test_main.py::TestRecommendEndpoint::test_recommend_invalid_field_type PASSED
test_main.py::TestRecommendEndpoint::test_recommend_field_out_of_range PASSED
test_main.py::TestRecommendEndpoint::test_recommend_ph_out_of_range PASSED
test_main.py::TestAdvancedRecommendEndpoint::test_advanced_requires_coordinates PASSED
test_main.py::TestAdvancedRecommendEndpoint::test_advanced_with_weather_api_success PASSED
test_main.py::TestAdvancedRecommendEndpoint::test_advanced_weather_fallback_no_api_key PASSED
test_main.py::TestAdvancedRecommendEndpoint::test_advanced_weather_api_failure_fallback PASSED
test_main.py::TestAdvancedRecommendEndpoint::test_advanced_weather_network_error PASSED
test_main.py::TestResponseSchema::test_recommend_response_structure PASSED
test_main.py::TestResponseSchema::test_fertilizer_recommendation_fields PASSED
test_main.py::TestEdgeCases::test_recommend_minimum_values PASSED
test_main.py::TestEdgeCases::test_recommend_maximum_values PASSED
test_main.py::TestEdgeCases::test_recommend_optional_fields PASSED

======================== 16 passed in 0.25s ========================
```

---

## Test Details

### test_health_returns_ok
Verifies the health check endpoint returns correct structure.

**Request:**
```bash
GET /
```

**Expected Response (200):**
```json
{
  "status": "ok",
  "service": "AgroAI API",
  "version": "1.0.0",
  "model_loaded": true
}
```

**Assertions:**
- `response.status_code == 200`
- `data["status"] == "ok"`
- All required fields present

---

### test_recommend_valid_payload
Verifies valid soil input returns complete recommendation response.

**Request:**
```bash
POST /recommend
{
  "N": 90, "P": 42, "K": 43, "ph": 6.5
}
```

**Expected Response (200):**
```json
{
  "soil_analysis": {
    "n_level": "Medium",
    "p_level": "Medium",
    "k_level": "Low",
    "ph_status": "Neutral",
    "health_score": 85.0,
    "health_label": "Excellent"
  },
  "crop_recommendation": {
    "crop": "Rice",
    "confidence": 0.87,
    "alternatives": ["Wheat", "Maize", "Sugarcane"]
  },
  "fertilizer_plan": [...],
  "alerts": [...],
  "weather_used": false
}
```

**Assertions:**
- All 5 top-level fields present
- All soil_analysis fields present and typed correctly
- Crop matches prediction
- Confidence between 0 and 1
- Alternatives is a list
- weather_used is false

---

### test_advanced_weather_api_failure_fallback
**Critical Test:** Verifies weather fallback works correctly.

**Request:**
```bash
POST /recommend-advanced
{
  "N": 90, "P": 42, "K": 43, "ph": 6.5,
  "latitude": 17.3850, "longitude": 78.4867
}
```

**Weather API:** Fails with timeout

**Expected Response (200):**
```json
{
  "weather_used": false,  // ← Fallback to false
  "alerts": [
    "⚠️ Weather data unavailable – using manual inputs",  // ← Warning alert
    ...other alerts...
  ],
  ...rest of response...
}
```

**Assertions:**
- `response.status_code == 200` (not 500)
- `data["weather_used"] == False`
- Warning alert in alerts list
- All response fields present

---

## Notes

- All tests use `mock_model_manager` to avoid ML model dependency
- Weather tests use `patch` to mock API calls
- Tests are isolated (no shared state between tests)
- Uses FastAPI `TestClient` (synchronous, no async/await needed)
- Follows pytest conventions: fixtures, parametrize, assertions

---

## Integration with CI/CD

Add to your CI/CD pipeline:
```bash
pytest test_main.py -v --tb=short
```

Or with coverage:
```bash
pytest test_main.py -v --cov=app --cov-report=term-missing
```

---

*Test Suite Created: 2026-04-23*  
*16 Tests | 5 Test Classes | 4 Fixtures*
