"""OpenWeather integration utilities for AgroAI."""

from __future__ import annotations

import logging
import os
from typing import Dict

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env when module is imported.
load_dotenv()


class WeatherAPIError(Exception):
    """Raised when weather data cannot be fetched or validated."""


def is_weather_available() -> bool:
    """Return True when OpenWeather API key is configured."""
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    return bool(api_key)


def fetch_weather(lat: float, lon: float) -> Dict[str, float | str]:
    """
    Fetch current weather from OpenWeather API for the given coordinates.

    Returns:
        Dictionary containing temperature, humidity, city, and description.

    Raises:
        WeatherAPIError: if API key is missing, request times out, HTTP fails,
        or response payload is malformed.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        message = "OPENWEATHER_API_KEY is not set. Configure it in environment or .env."
        logger.error(message)
        raise WeatherAPIError(message)

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.Timeout as exc:
        message = "OpenWeather request timed out after 10 seconds."
        logger.exception(message)
        raise WeatherAPIError(message) from exc
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        body = exc.response.text if exc.response is not None else ""
        message = f"OpenWeather HTTP error ({status_code}): {body}"
        logger.exception(message)
        raise WeatherAPIError(message) from exc
    except requests.RequestException as exc:
        message = f"OpenWeather request failed: {exc}"
        logger.exception(message)
        raise WeatherAPIError(message) from exc

    try:
        data = response.json()
        weather_payload = {
            "temperature": float(data["main"]["temp"]),
            "humidity": float(data["main"]["humidity"]),
            "city": str(data.get("name", "")),
            "description": str(data["weather"][0]["description"]),
        }
        return weather_payload
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        message = "Unexpected OpenWeather response format."
        logger.exception(message)
        raise WeatherAPIError(message) from exc

