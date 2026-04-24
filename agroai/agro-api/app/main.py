"""FastAPI backend for AgroAI crop and fertilizer recommendations."""

from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.model import model_manager
from app.schemas import CropRecommendation, RecommendResponse, SoilInput
from app.sensor import get_mock_sensor_data
from app.services import analyze_soil, calculate_fertilizer_plan, generate_alerts
from app.weather import WeatherAPIError, fetch_weather, is_weather_available

# Configure Python logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Load model on startup, clean up on shutdown."""
    logger.info("Starting AgroAI API service...")
    try:
        model_manager.load()
        logger.info("✓ ML model loaded successfully.")
    except Exception as exc:
        logger.error("✗ Failed to load ML model: %s", exc)
        # Continue startup; some endpoints may work without model.

    yield

    logger.info("Shutting down AgroAI API service.")


# Initialize FastAPI app with metadata and lifespan.
app = FastAPI(
    title="AgroAI API",
    description="Intelligent crop and fertilizer recommendations using ML and soil analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for mobile/frontend development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AgroAI API",
        "version": "1.0.0",
        "model_loaded": model_manager.is_loaded(),
    }


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(soil_input: SoilInput) -> RecommendResponse:
    """
    Basic crop recommendation based on soil nutrients and optional climate.

    Endpoint flow:
    1. Validate input (Pydantic)
    2. Predict crop using ML model
    3. Analyze soil health
    4. Calculate fertilizer plan
    5. Generate alerts
    6. Return complete recommendation

    Args:
        soil_input: SoilInput model with N, P, K, pH, optional temp/humidity

    Returns:
        RecommendResponse with crop, soil analysis, fertilizer plan, alerts
    """
    logger.info("POST /recommend called with input: N=%s, P=%s, K=%s, pH=%s",
                soil_input.N, soil_input.P, soil_input.K, soil_input.ph)

    try:
        # Run ML prediction.
        prediction = model_manager.predict(soil_input)
        logger.info("Crop prediction: %s (confidence: %.2f%%)",
                    prediction["crop"], prediction["confidence"] * 100)

        # Analyze soil health.
        soil_analysis = analyze_soil(soil_input)
        logger.info("Soil analysis: %s (health_score=%.1f)",
                    soil_analysis.health_label, soil_analysis.health_score)

        # Calculate fertilizer needs.
        fertilizer_plan = calculate_fertilizer_plan(soil_input, prediction["crop"])
        logger.info("Fertilizer plan: %d recommendations", len(fertilizer_plan))

        # Generate alerts and warnings.
        alerts = generate_alerts(soil_input, prediction["crop"], soil_analysis)
        logger.info("Alerts generated: %d messages", len(alerts))

        response = RecommendResponse(
            soil_analysis=soil_analysis,
            crop_recommendation=CropRecommendation(
                crop=prediction["crop"],
                confidence=prediction["confidence"],
                alternatives=prediction["alternatives"],
            ),
            fertilizer_plan=fertilizer_plan,
            alerts=alerts,
            weather_used=False,
        )
        logger.info("✓ /recommend response complete")
        return response

    except ValidationError as exc:
        logger.warning("Validation error in /recommend: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input: {exc.error_count()} validation error(s)",
        ) from exc
    except Exception as exc:
        logger.exception("Internal error in /recommend: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


@app.post("/recommend-advanced", response_model=RecommendResponse)
async def recommend_advanced(soil_input: SoilInput) -> RecommendResponse:
    """
    Advanced crop recommendation with weather data integration.

    Requires latitude and longitude in request. Fetches real-time weather
    from OpenWeather API and injects temperature/humidity into recommendation flow.

    Endpoint flow:
    1. Validate latitude and longitude are provided
    2. Fetch weather data
    3. Inject weather data into soil input
    4. Run standard recommendation flow
    5. Return RecommendResponse with weather_used=True

    If weather fetch fails, falls back to standard /recommend with warning alert.

    Args:
        soil_input: SoilInput with latitude, longitude, and soil nutrients

    Returns:
        RecommendResponse with crop, soil analysis, fertilizer plan, alerts
    """
    logger.info("POST /recommend-advanced called with input: N=%s, P=%s, K=%s, pH=%s, "
                "lat=%s, lon=%s",
                soil_input.N, soil_input.P, soil_input.K, soil_input.ph,
                soil_input.latitude, soil_input.longitude)

    # Validate coordinates.
    if soil_input.latitude is None or soil_input.longitude is None:
        logger.warning("Missing coordinates in /recommend-advanced")
        raise HTTPException(
            status_code=422,
            detail="latitude and longitude are required for /recommend-advanced",
        )

    weather_used = False
    alerts_list: List[str] = []

    try:
        # Attempt to fetch weather data.
        if is_weather_available():
            try:
                weather = fetch_weather(soil_input.latitude, soil_input.longitude)
                logger.info("✓ Weather fetched: temp=%.1f°C, humidity=%.1f%%, city=%s",
                            weather["temperature"], weather["humidity"], weather["city"])

                # Create a copy with injected weather data (don't mutate input).
                soil_with_weather = soil_input.model_copy(update={
                    "temperature": weather["temperature"],
                    "humidity": weather["humidity"],
                })
                weather_used = True

            except WeatherAPIError as exc:
                logger.warning("Weather fetch failed, using fallback: %s", exc)
                soil_with_weather = soil_input
                alerts_list.append("⚠️ Weather data unavailable – using manual inputs")
        else:
            soil_with_weather = soil_input

        # Run standard recommendation flow.
        prediction = model_manager.predict(soil_with_weather)
        logger.info("Crop prediction: %s (confidence: %.2f%%)",
                    prediction["crop"], prediction["confidence"] * 100)

        soil_analysis = analyze_soil(soil_with_weather)
        logger.info("Soil analysis: %s (health_score=%.1f)",
                    soil_analysis.health_label, soil_analysis.health_score)

        fertilizer_plan = calculate_fertilizer_plan(soil_with_weather, prediction["crop"])
        logger.info("Fertilizer plan: %d recommendations", len(fertilizer_plan))

        alerts = generate_alerts(soil_with_weather, prediction["crop"], soil_analysis)
        alerts.extend(alerts_list)
        logger.info("Alerts generated: %d messages", len(alerts))

        response = RecommendResponse(
            soil_analysis=soil_analysis,
            crop_recommendation=CropRecommendation(
                crop=prediction["crop"],
                confidence=prediction["confidence"],
                alternatives=prediction["alternatives"],
            ),
            fertilizer_plan=fertilizer_plan,
            alerts=alerts,
            weather_used=weather_used,
        )
        logger.info("✓ /recommend-advanced response complete (weather_used=%s)", weather_used)
        return response

    except HTTPException:
        raise
    except ValidationError as exc:
        logger.warning("Validation error in /recommend-advanced: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input: {exc.error_count()} validation error(s)",
        ) from exc
    except Exception as exc:
        logger.exception("Internal error in /recommend-advanced: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


@app.post("/sensor-recommend")
async def sensor_recommend() -> Dict[str, Any]:
    """
    Sensor mode: Get mock sensor data and return recommendation.
    
    This endpoint simulates a real soil sensor providing data automatically.
    No request body needed - sensor data is generated internally.
    
    Endpoint flow:
    1. Generate mock sensor data
    2. Run standard recommendation flow
    3. Return recommendation with sensor data included
    
    Returns:
        Dict with sensor_data and recommendation fields
    """
    logger.info("POST /sensor-recommend called")
    
    try:
        # Generate mock sensor data
        sensor_data = get_mock_sensor_data()
        logger.info("Mock sensor data generated: N=%.1f, P=%.1f, K=%.1f, pH=%.1f",
                    sensor_data.N, sensor_data.P, sensor_data.K, sensor_data.ph)
        
        # Run ML prediction
        prediction = model_manager.predict(sensor_data)
        logger.info("Crop prediction: %s (confidence: %.2f%%)",
                    prediction["crop"], prediction["confidence"] * 100)
        
        # Analyze soil health
        soil_analysis = analyze_soil(sensor_data)
        logger.info("Soil analysis: %s (health_score=%.1f)",
                    soil_analysis.health_label, soil_analysis.health_score)
        
        # Calculate fertilizer needs
        fertilizer_plan = calculate_fertilizer_plan(sensor_data, prediction["crop"])
        logger.info("Fertilizer plan: %d recommendations", len(fertilizer_plan))
        
        # Generate alerts
        alerts = generate_alerts(sensor_data, prediction["crop"], soil_analysis)
        logger.info("Alerts generated: %d messages", len(alerts))
        
        recommendation = RecommendResponse(
            soil_analysis=soil_analysis,
            crop_recommendation=CropRecommendation(
                crop=prediction["crop"],
                confidence=prediction["confidence"],
                alternatives=prediction["alternatives"],
            ),
            fertilizer_plan=fertilizer_plan,
            alerts=alerts,
            weather_used=False,
        )
        logger.info("✓ /sensor-recommend response complete")
        
        return {
            "sensor_data": sensor_data,
            "recommendation": recommendation,
        }
    
    except Exception as exc:
        logger.exception("Internal error in /sensor-recommend: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(exc)}",
        ) from exc
async def validation_exception_handler(request: Any, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors with clean JSON response."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"][1:]),
            "message": error["msg"],
        })
    logger.warning("Request validation failed: %s", errors)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Any, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions with 500 response."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc),
        },
    )
