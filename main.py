import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OpenWeather_API_KEY")


def get_weather(city):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")

    if r.status_code != 200:
        print('Error Occured') 
    
    data = r.json()  # Cleaning the data to add to a pandas df

    print(data)



get_weather("Colombo")