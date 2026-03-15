"""
ClimaShield – Weather Service
Fetches real-time environmental data from OpenWeatherMap API.
"""

import httpx
import logging
from typing import Optional

from app.config import settings


logger = logging.getLogger("climashield.weather")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def fetch_weather(city: str) -> dict:
    """
    Fetch current weather data for a given city from OpenWeatherMap.

    Returns:
        {
            "city": "Mumbai",
            "rain_mm": 42.0,
            "temperature": 29.0,
            "humidity": 88,
            "source": "openweathermap" | "mock"
        }
    """
    if not settings.weather_api_key:
        logger.info(f"[MOCK] No API key configured – using mock data for {city}")
        result = _mock_weather(city)
        result["source"] = "mock"
        return result

    # Try fetching real data from OpenWeatherMap
    try:
        params = {
            "q": city,
            "appid": settings.weather_api_key,
            "units": "metric",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(OPENWEATHER_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        result = _parse_weather_response(city, data)
        result["source"] = "openweathermap"
        logger.info(f"[LIVE] Fetched real weather for {city}: {result}")
        return result

    except httpx.HTTPStatusError as e:
        logger.warning(
            f"[API ERROR] OpenWeatherMap returned {e.response.status_code} for {city}: "
            f"{e.response.text} – falling back to mock data"
        )
        result = _mock_weather(city)
        result["source"] = "mock (api_error)"
        return result

    except Exception as e:
        logger.warning(f"[ERROR] Failed to fetch weather for {city}: {e} – falling back to mock data")
        result = _mock_weather(city)
        result["source"] = "mock (error)"
        return result


def _parse_weather_response(city: str, data: dict) -> dict:
    """Parse raw OpenWeatherMap response into ClimaShield format."""
    rain_mm = 0.0
    if "rain" in data:
        # OpenWeatherMap provides rain in mm for last 1h or 3h
        rain_mm = data["rain"].get("1h", data["rain"].get("3h", 0.0))

    # AQI: OpenWeatherMap doesn't include it in the weather endpoint,
    # so we estimate from visibility + humidity (higher = worse air)
    visibility = data.get("visibility", 10000)
    humidity = data["main"]["humidity"]
    # Lower visibility & higher humidity → worse AQI (rough heuristic)
    aqi_estimate = max(50, int(400 - (visibility / 30) + (humidity * 0.5)))

    return {
        "city": city,
        "rain_mm": round(rain_mm, 2),
        "temperature": round(data["main"]["temp"], 2),
        "humidity": humidity,
        "aqi": aqi_estimate,
    }


def _mock_weather(city: str) -> dict:
    """
    Return realistic mock weather data for development/testing.
    AQI values based on real Indian city air quality trends.
    """
    mock_data = {
        "mumbai": {"city": "Mumbai", "rain_mm": 42.0, "temperature": 29.0, "humidity": 88, "aqi": 180},
        "delhi": {"city": "Delhi", "rain_mm": 5.0, "temperature": 38.0, "humidity": 45, "aqi": 320},
        "chennai": {"city": "Chennai", "rain_mm": 30.0, "temperature": 33.0, "humidity": 78, "aqi": 145},
        "kolkata": {"city": "Kolkata", "rain_mm": 25.0, "temperature": 31.0, "humidity": 82, "aqi": 210},
        "bangalore": {"city": "Bangalore", "rain_mm": 15.0, "temperature": 26.0, "humidity": 65, "aqi": 120},
        "lucknow": {"city": "Lucknow", "rain_mm": 8.0, "temperature": 35.0, "humidity": 50, "aqi": 340},
        "patna": {"city": "Patna", "rain_mm": 10.0, "temperature": 34.0, "humidity": 55, "aqi": 290},
        "kanpur": {"city": "Kanpur", "rain_mm": 6.0, "temperature": 36.0, "humidity": 48, "aqi": 360},
    }

    key = city.lower()
    if key in mock_data:
        return mock_data[key]

    # Default fallback for unknown cities
    return {
        "city": city,
        "rain_mm": 20.0,
        "temperature": 30.0,
        "humidity": 70,
        "aqi": 200,
    }
