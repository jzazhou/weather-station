#!/usr/bin/env python3
import requests
from datetime import datetime

from config import OWM_API_KEY, CITY_NAME, COUNTRY_CODE, UNITS

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_outdoor_weather():

    params = {
        "q": f"{CITY_NAME},{COUNTRY_CODE}",
        "appid": OWM_API_KEY,
        "units": UNITS,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("[weather_api] Request timed out after 10 seconds.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[weather_api] HTTP error from OpenWeatherMap: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[weather_api] Network error: {e}")
        return None

    data = response.json()

    try:
        weather = {
            "temp":         data["main"]["temp"],
            "feels_like":   data["main"]["feels_like"],
            "humidity":     data["main"]["humidity"],
            "pressure":     data["main"]["pressure"],
            "description":  data["weather"][0]["description"].title(),
            "icon_code":    data["weather"][0]["icon"],
            "condition_id": data["weather"][0]["id"],
            "wind_speed":   data["wind"]["speed"],
            "city":         data["name"],
            "updated_at":   datetime.now(),
        }
    except (KeyError, IndexError) as e:
        print(f"[weather_api] Unexpected response structure: {e}")
        return None

    return weather


if __name__ == "__main__":
    print("Fetching outdoor weather...\n")
    result = fetch_outdoor_weather()

    if result is None:
        print("Fetch failed. See the error message above.")
    else:
        print(f"Location:      {result['city']}")
        print(f"Condition:     {result['description']}")
        print(f"Temperature:   {result['temp']:.1f} °C")
        print(f"Feels like:    {result['feels_like']:.1f} °C")
        print(f"Humidity:      {result['humidity']} %")
        print(f"Pressure:      {result['pressure']} hPa")
        print(f"Wind speed:    {result['wind_speed']:.1f} m/s")
        print(f"Icon code:     {result['icon_code']}")
        print(f"Fetched at:    {result['updated_at'].strftime('%H:%M:%S')}")