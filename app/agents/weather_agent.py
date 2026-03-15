"""
ClimaShield – Weather Oracle Agent (OpenClaw)
Fetches real-time environmental data for insurance evaluation.
"""

from app.services.weather_service import fetch_weather


class WeatherOracleAgent:
    """
    OpenClaw agent that acts as a weather data oracle.
    Fetches real-time environmental metrics from OpenWeatherMap
    and returns standardized data for trigger evaluation.
    """

    agent_type = "weather_oracle"
    description = "Fetches real-time weather and environmental data"

    async def get_weather(self, city: str) -> dict:
        """
        Fetch current weather data for a city.

        Args:
            city: Name of the city to fetch weather for.

        Returns:
            {
                "city": "Mumbai",
                "rain_mm": 42.0,
                "temperature": 29.0,
                "humidity": 88
            }
        """
        return await fetch_weather(city)

    async def get_rainfall(self, city: str) -> float:
        """Get current rainfall in mm for a city."""
        data = await fetch_weather(city)
        return data["rain_mm"]

    async def get_temperature(self, city: str) -> float:
        """Get current temperature in °C for a city."""
        data = await fetch_weather(city)
        return data["temperature"]

    async def get_humidity(self, city: str) -> int:
        """Get current humidity percentage for a city."""
        data = await fetch_weather(city)
        return data["humidity"]
