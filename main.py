import requests
import os
from dotenv import load_dotenv
import pandas as pd
import dash
from dash import Dash, html,dcc, Input ,Output, State
import plotly.express as px
import dash_bootstrap_components as dbc


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
            "humidity":entry["main"]["humidity"],
            "wind":entry["wind"]["speed"]
        })

    return pd.DataFrame(forecast_dict), data["city"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Welcome to the Weather APP"),

    html.Div([
        dcc.Input(id="city-name", type="text", placeholder="Enter City"),
        html.Button("Search", id="search-btn", n_clicks=0),
        
    ]),
    html.Div(id="current-weather"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="temp-graph"),
                    dcc.Slider(id="temp-slider", min = 0, max=50, step=1, value= 50, marks={0:"0°C",10:"10°C",20:"20°C",30:"30°C",40:"40°C",50:"50°C"}),

                ])
            ])
        ])
        
    ]),
   
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="humidity-graph")
                ])
            ])
        ], width=6 ),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="wind-graph")
                ])
            ])
        ], width=6)

        
    ]),
    dcc.Graph(id="map-view")
])


@app.callback(
    Output("current-weather", "children"),
    Output("humidity-graph", "figure"),
    Output("wind-graph", "figure"),
    Output("map-view", "figure"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value")
)
def update_weather(n, city):
    data = get_weather(city)
    if data is None:
        return "City Not Found Please Try again!"
    
    df, city_info = data

    
    current_weather_data = df.iloc[0]
    weather_data = html.Div([
        html.H3(f"{city} Current Time: {current_weather_data['time']}"),
        html.P(f"{current_weather_data['weather' ]} | {current_weather_data['temp']} |")
    ])

    humidity_fig = px.line(df, x="time", y="humidity", title="Humidity Over Time")
    wind_fig =  px.line(df, x="time", y="wind", title="Wind Speed Over Time")

    map_fig = px.scatter_mapbox(lat=[city_info["coord"]["lat"]], lon=[city_info["coord"]["lon"]], text=[city_info["name"]], zoom=6)
    map_fig.update_layout(mapbox_style="open-street-map")


    return weather_data, humidity_fig, wind_fig, map_fig

@app.callback(
    Output("temp-graph", "figure"),
    Input("temp-slider", "value"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value")
)

def update_temp_graph(max_temp, n_clicks, city):
    df,_ = get_weather(city)

    filter_data = df[df["temp"] <= max_temp]
    temp_fig = px.histogram(filter_data, x="temp", nbins=10, title= f"Temperature Graph ({max_temp})")
    
    return temp_fig

if __name__ == '__main__':
    app.run(debug=True)