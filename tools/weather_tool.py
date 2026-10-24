
import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city: str) -> dict:
    """
    Retrieve current weather for a city.

    Args:
        city: Name of the city.

    Returns:
        A dictionary containing location and weather information.
    """

    if not city or not city.strip():
        raise ValueError("City name cannot be empty.")

    # Step 1: Find the city's geographic coordinates.
    location_response = requests.get(
        GEOCODING_URL,
        params={
            "name": city.strip(),
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    location_response.raise_for_status()
    location_data = location_response.json()

    locations = location_data.get("results", [])

    if not locations:
        raise ValueError(f"Could not find the city: {city}")

    location = locations[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Step 2: Request the current weather.
    weather_response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto",
        },
        timeout=10,
    )

    weather_response.raise_for_status()
    weather_data = weather_response.json()

    current = weather_data.get("current")

    if not current:
        raise RuntimeError("Weather data is unavailable.")

    return {
        "city": location["name"],
        "country": location.get("country", "Unknown"),
        "temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
        "observed_at": current["time"],
        "timezone": weather_data.get("timezone", "Unknown"),
    }


def describe_weather_code(code: int) -> str:
    """Convert a WMO weather code into a readable description."""

    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return descriptions.get(code, "Unknown conditions")
