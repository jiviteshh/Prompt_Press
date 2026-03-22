# weather_utils.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city_name):
    if not OPENWEATHER_API_KEY:
        raise ValueError("Missing OPENWEATHER_API_KEY")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city_name}&units=metric&appid={OPENWEATHER_API_KEY}"
    )
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return None

        weather = {
            "city": data["name"],
            "temp": round(data["main"]["temp"]),
            "condition": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "wind": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
        return weather

    except Exception as e:
        print("Weather Error:", e)
        return None

def get_weather_nlg(weather):
    """Generate natural language weather summary"""
    condition = weather["condition"]
    city = weather["city"]
    temp = weather["temp"]
    return (
        f"It's a {condition.lower()} day in {city}, {temp}°C – "
        f"{'great day for a stroll!' if temp > 20 else 'don’t forget your jacket!'}"
    )
