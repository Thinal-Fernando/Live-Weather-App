import requests
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime,timezone, timedelta

load_dotenv()
api_key = os.getenv("OpenWeather_API_KEY")

def get_weather(city, units = "metric"):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}")

    if r.status_code != 200:
        return None
    
    data = r.json()
    timezone_offset = data["city"]["timezone"]

    forecast_dict = []
    for entry in data["list"]:

        utc_time = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
        local_time = utc_time + timedelta(seconds=timezone_offset)

        forecast_dict.append({
            "time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temp": entry["main"]["temp"],
            "weather": entry["weather"][0]["main"],
            "humidity": entry["main"]["humidity"],
            "wind": entry["wind"]["speed"],
            "icon": entry["weather"][0]["icon"]
        })

    return pd.DataFrame(forecast_dict), data["city"]
