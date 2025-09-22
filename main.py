import requests
import os
from dotenv import load_dotenv
import pandas as pd
import dash
from dash import Dash, html,dcc, Input ,Output, State
import plotly.express as px


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
            "weather": entry["weather"][0]["main"],
            "humidity":entry["main"]["humidity"]
        })

    return pd.DataFrame(forecast_dict)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Welcome to the Weather APP"),

    html.Div([
        dcc.Input(id="city-name", type="text", placeholder="Enter City"),
        html.Button("Search", id="search-btn", n_clicks=0),
        
    ]),
    html.Div(id="current-weather"),

    dcc.Graph(id="temp-graph"),
    dcc.Slider(id="temp-slider", min = 0, max=50, step=1, value= 50, marks={0:"0°C",10:"10°C",20:"20°C",30:"30°C",40:"40°C",50:"50°C"}),

    dcc.Graph(id="humidity-Graph")
])


@app.callback(
    Output("current-weather", "children"),
    Output("humidity-Graph", "figure"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value")
)
def update_weather(n, city):
    data = get_weather(city)
    if data is None:
        return "City Not Found Please Try again!"
    
    current_weather_data = data.iloc[0]
    weather_data = html.Div([
        html.H3(f"{city} Current Time: {current_weather_data['time']}"),
        html.P(f"{current_weather_data['weather' ]} | {current_weather_data['temp']} |")
    ])

    humidity_fig = px.line(data, x="time", y="humidity", title="Temperature Over Time")
    

    return weather_data, humidity_fig

@app.callback(
    Output("temp-graph", "figure"),
    Input("temp-slider", "value"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value")
)

def update_temp_graph(max_temp, n_clicks, city):
    df = get_weather(city)

    filter_data = df[df["temp"] <= max_temp]
    temp_fig = px.histogram(filter_data, x="temp", nbins=10, title= f"Temperature Graph ({max_temp})")
    
    return temp_fig

if __name__ == '__main__':
    app.run(debug=True)