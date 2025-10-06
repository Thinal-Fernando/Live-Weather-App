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


def get_weather(city, units = "metric"):
    r = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}")

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
            "wind":entry["wind"]["speed"],
            "icon": entry["weather"][0]["icon"]
        })

    return pd.DataFrame(forecast_dict), data["city"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.sidebar = dbc.Offcanvas([
        html.H5("Options", className="mb-3"),

        html.Hr(),

        dbc.Button("Home", id="btn-clouds", color="secondary", className="mb-2", n_clicks=0),

        dbc.Button("Details", id="btn-rain", color="primary", className="mb-2", n_clicks=0),


    ],id="sidebar", placement="start", is_open=False,
)




app.layout = dbc.Container([
    dbc.Row([
        
        dbc.Col([
            html.H1(id="heading"),

            dbc.Button("☰ Menu", id="menu-button", color="dark", className="mb-3"),

            app.sidebar,
            
            html.Div([
                
                dcc.Graph(id="map-view", style={"height": "700px"}),

                dbc.ButtonGroup([
                    dbc.Button(" 🌡 Temperature", id="temp-overlay", n_clicks=0,color="info", className="mb-3"),
                    dbc.Button(" 🌧 Precipitation", id="precipitation-overlay", n_clicks=0,color="info", className="mb-3"), 
                    dbc.Button(" 🕛 Pressure", id="pressure-overlay", n_clicks=0,color="info", className="mb-3"), 
                    dbc.Button(" 💨 Wind speed", id="wind-overlay", n_clicks=0,color="info", className="mb-3"), 
                    dbc.Button(" ☁︎ Clouds", id="cloud-overlay", n_clicks=0,color="info", className="mb-3"),
                ], size="sm", className="button-group", style={
                    "position": "absolute",
                    "bottom": "15px",
                    "left": "29%",
                    "zIndex": "999"
                }),

            ], style={"position": "relative"}),
            
            
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
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="wind-graph")
                        ])
                    ])
                ], width=6)

                
            ]),

            dbc.Row([
                html.H3("Hourly Forecast", className="mt-4 mb-3 text-center"),
                html.Div(id="hourly-cards", className="d-flex flex-wrap justify-content-center gap-3 mb-5")


            ])

        ], width=9),


        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Check the weather forecast", style={"fontWeight": "bold", "fontSize": "18px", "textAlign": "center", "padding": "10px"}),

                html.Div([
                dcc.Input(id="city-name", type="text", placeholder="Enter City..."),
                html.Button("Search", id="search-btn", n_clicks=0),
                
                ], className="mt-5 ms-3"),

                dbc.CardBody([ 
                    dbc.RadioItems(
                        id="unit-selector",
                        options=[
                            {"label": "Celsius (°C)", "value": "metric"},
                            {"label": "Fahrenheit (°F)", "value": "imperial"}
                        ],
                        value = "metric", inline=True
                    ),

                    html.Div(id="current-weather", className="w-100"),
                ], style={" width":"100% "})
               
            ], style={"height" : "100%"})
        ],width=3),

    ])
    
    
], fluid=True)


@app.callback(
    Output("sidebar", "is_open"),
    Input("menu-button", "n_clicks"),
    State("sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output("heading", "children"),
    Output("current-weather", "children"),
    Output("humidity-graph", "figure"),
    Output("wind-graph", "figure"),
    Output("map-view", "figure"),
    Output("hourly-cards", "children"),
    Input("search-btn", "n_clicks"),
    Input("temp-overlay", "n_clicks"),
    Input("precipitation-overlay", "n_clicks"),
    Input("pressure-overlay", "n_clicks"),
    Input("wind-overlay", "n_clicks"),
    Input("cloud-overlay", "n_clicks"),
    Input("unit-selector", "value"),
    State("city-name", "value")
    
)
def update_weather(n,  temp_clicks, precipitation_clicks, pressure_clicks, wind_clicks, cloud_clicks, units, city):
    data = get_weather(city, units)
    if data is None:
        return "City Not Found Please Try again!"
    
    df, city_info = data

    heading = html.H1([ "Welcome to the Weather APP" if city is None else f"Viewing: {city}" ])

    current_weather_data = df.iloc[0]

    unit_symbol = "°C" if units == "metric" else "°F"

    weather_stats = [
        {"emoji": "🍃", "value": f"{round(current_weather_data['wind'], 1)} km/h"},
        {"emoji": "💧", "value": f"{current_weather_data['humidity']}%"},
    ]

    weather_data = html.Div(
        className="row d-flex justify-content-center py-5",
        children=[
            html.Div(  
                children=[
                    html.Div(
                        className="card text-body",
                        style={"border-radius": "20px"},
                        children=[
                            html.Div(
                                className="card-body p-3",
                                children=[
                
                                    html.Div(
                                        className="d-flex",
                                        children=[
                                            html.H6(city, className="flex-grow-1"),
                                            html.H6(current_weather_data["time"].split(" ")[1])
                                        ]
                                    ),
                                    html.Div(
                                        className="d-flex flex-column text-center mt-3 mb-3",
                                        children=[
                                            html.H6(f"{round(current_weather_data['temp'],1)}{unit_symbol}",
                                                    style={"font-size": "2rem", "font-weight": "bold"}),
                                            html.Span(current_weather_data["weather"],
                                                    className="small", style={"color": "#868B94"})
                                        ]
                                    ),
                               
                                    html.Div(
                                        className="d-flex align-items-center",
                                        children=[
                                            html.Div(
                                                className="flex-grow-1",
                                                style={"font-size": "0.9rem"},
                                                children=[
                                                    html.Div(f"{stat['emoji']} {stat['value']}", className="mb-1")
                                                    for stat in weather_stats
                                                ]
                                            ),
                                            html.Div(
                                                children=html.Img(
                                                    src=f"http://openweathermap.org/img/wn/{current_weather_data['icon']}@2x.png",
                                                    width="70px"
                                                )
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

    hourly_cards = []
    for _, row in df.head(8).iterrows():
        card_data = dbc.Card([
            dbc.CardBody([
                html.H6(row["time"].split(" ")[1],className="text-center" ),
                html.Img(
                    src=f"http://openweathermap.org/img/wn/{row['icon']}@2x.png",
                    style={"width": "50px", "margin": "auto"}
                ),
                html.H6(f"{round(row['temp'], 1)}{unit_symbol}", className="text-center mt-2"),
                html.Small(row["weather"], className="text-center d-block text-muted")
            ])
        ])
        hourly_cards.append(card_data)



    humidity_fig = px.line(df, x="time", y="humidity", title="Humidity Over Time")
    wind_fig =  px.line(df, x="time", y="wind", title="Wind Speed Over Time")

    ctx = dash.callback_context
    overlay_url = None
    zoom_level = 10

    map_fig = px.scatter_mapbox(lat=[city_info["coord"]["lat"]], lon=[city_info["coord"]["lon"]], height=700,
                            hover_data={
                                "City": [city_info["name"]],
                                "Temperature (C)" : [df.iloc[0]["temp"]],
                                "Weather": [df.iloc[0]["weather"]],
                                "Humidity (%)": [df.iloc[0]["humidity"]],
                                "Wind (m/s)": [df.iloc[0]["wind"]],
                            } )
    map_fig.update_layout(mapbox_style="open-street-map")

    
    layer_urls = {
        "temp-overlay": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "precipitation-overlay": f"https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "pressure-overlay": f"https://tile.openweathermap.org/map/pressure_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "wind-overlay": f"https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "cloud-overlay": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}"
    }



    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id in layer_urls:
            overlay_url = layer_urls[button_id]
            zoom_level = 5

    
    map_fig.update_layout(
    mapbox={
        "zoom": zoom_level,
        "layers": [
            {
                "sourcetype": "raster",
                "source": [overlay_url],
                "below": "traces"
            }
        ] if overlay_url else []
    }
)
     

    return heading, weather_data, humidity_fig, wind_fig, map_fig, hourly_cards

@app.callback(
    Output("temp-graph", "figure"),
    Input("temp-slider", "value"),
    Input("search-btn", "n_clicks"),
    State("city-name", "value"),
    State("unit-selector", "value")
)

def update_temp_graph(max_temp, n_clicks, city, units):
    df,_ = get_weather(city, units)

    filter_data = df[df["temp"] <= max_temp]
    temp_fig = px.histogram(filter_data, x="temp", nbins=10, title= f"Temperature Graph ({max_temp})")
    
    return temp_fig


if __name__ == '__main__':
    app.run(debug=True)