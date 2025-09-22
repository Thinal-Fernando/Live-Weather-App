import requests
import os
from dotenv import load_dotenv
import pandas as pd
import dash
from dash import Dash, html


load_dotenv()
api_key = os.getenv("OpenWeather_API_KEY")


def get_weather(city):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")

    if r.status_code != 200:
        print('Error Occured') 
    
    data = r.json()  # Cleaning the data to add to a pandas df

    forecast_dict = []
    for entry in data["list"]:
        forecast_dict.append({
            "time": entry["dt_txt"],
            "temp": entry["main"]["temp"],
            "weather": entry["weather"][0]["main"]
        })

    return pd.DataFrame(forecast_dict)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Test")
])


if __name__ == '__main__':
    app.run(debug=True)