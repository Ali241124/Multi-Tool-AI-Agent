import requests
from tools.weather_tool import get_weather, describe_weather_code


city = input("Enter a city name: ").strip()

try:
    weather = get_weather(city)

    print("\n--- Current Weather ---")
    print(f"Location: {weather['city']}, {weather['country']}")
    print(
        f"Temperature: {weather['temperature_c']} °C"
    )
    print(
        f"Feels like: {weather['feels_like_c']} °C"
    )
    print(
        f"Humidity: {weather['humidity_percent']}%"
    )
    print(
        f"Wind speed: {weather['wind_speed_kmh']} km/h"
    )
    print(
        "Conditions:",
        describe_weather_code(weather["weather_code"]),
    )
    print(f"Observed at: {weather['observed_at']}")
    print(f"Timezone: {weather['timezone']}")

except (ValueError, requests.RequestException) as error:
    print("Could not retrieve weather:", error)
except (KeyError, RuntimeError) as error:
    print("Unexpected weather response:", error)
