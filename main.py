import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OpenWeather_API_KEY")
city= "Colombo"
r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")

print(r.text)