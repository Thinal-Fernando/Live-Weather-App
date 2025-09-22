import requests
import os
from dotenv import load_dotenv
import pandas as pd
import dash
from dash import Dash, html,dcc, Input ,Output, State


load_dotenv()
api_key = os.getenv("OpenWeather_API_KEY")


def get_weather(city):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")

    if r.status_code != 200:
        return None
    
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
    html.H1("Welcome to the Weather APP"),

    html.Div([
        dcc.Input(id="city-name", type="text", placeholder="Enter City"),
        html.Button("Search", id="search-btn", n_clicks=0),
        html.Div(id="current-weather")
    ])
])


@app.callback(
    Output("current-weather", "children"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value")
)
def update(n, city):
    data = get_weather(city)
    if data is None:
        return "City Not Found Please Try again!"
    
    current_weather_data = data.iloc[0]
    weather_data = html.Div([
        html.H3(f"{city}"),
        html.P(f"{current_weather_data['weather' ]} | {current_weather_data['temp']} |")
    ])

    return weather_data


if __name__ == '__main__':
    app.run(debug=True)