import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import get_weather, api_key
import pandas as pd
from datetime import datetime,timezone, timedelta

dash.register_page(__name__, path='/', name='Home')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1(id="heading"),
            dbc.Button("☰ Menu", id="menu-button", color="dark", className="mb-3"),


            dbc.Offcanvas([
                html.H5("Options", className="mb-3"),
                html.Hr(),
                dbc.Button("Home", href="/", id="btn-clouds", color="secondary", className="mb-2", n_clicks=0),  
                dbc.Button("Details", href="/stats",  id="btn-rain", color="primary", className="mb-2",  n_clicks=0),  
            ], id="sidebar-home", placement="start", is_open=False),

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
    
    dbc.Row([
        dbc.Col([
            

            html.H3("Hourly Forecast", className="mt-4 mb-3 text-center"),
            html.Div(id="hourly-cards", className="d-flex gap-3 mb-5 hourly_cards_container"),
        ])
    ])

        

    ])
], fluid=True)



@dash.callback(
    Output("sidebar-home", "is_open"),
    Input("menu-button", "n_clicks"),
    State("sidebar-home", "is_open"),
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open


@dash.callback(
    Output("heading", "children"),
    Output("current-weather", "children"),
    Output("map-view", "figure"),
    Output("hourly-cards", "children"),
    Output("shared-city-data", "data"),
    Input("search-btn", "n_clicks"),
    Input("temp-overlay", "n_clicks"),
    Input("precipitation-overlay", "n_clicks"),
    Input("pressure-overlay", "n_clicks"),
    Input("wind-overlay", "n_clicks"),
    Input("cloud-overlay", "n_clicks"),
    Input("unit-selector", "value"),
    State("city-name", "value")
)
def update_weather(n, temp_clicks, precipitation_clicks, pressure_clicks, wind_clicks, cloud_clicks, units, city):
    data = get_weather(city, units)
    if not data:
        return "City Not Found", "", {}, [], None

    df, city_info = data

    timezone_offset = city_info["timezone"]
    utc_now = datetime.now(timezone.utc)
    local_time = utc_now + timedelta(seconds=timezone_offset)
    local_time_str = local_time.strftime("%a %I:%M %p") 


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
                                            html.H6(local_time_str)
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
    for _, row in df.head(24).iterrows():
        local_time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S")
        formatted_time = local_time.strftime("%a %I %p").lstrip("0")

        card_data = dbc.Card([
            dbc.CardBody([
                html.H6(formatted_time,className="text-center" ),
                html.Img(
                    src=f"http://openweathermap.org/img/wn/{row['icon']}@2x.png", 
                    style={"width": "50px", "margin": "auto"}
                ),
                html.H6(f"{round(row['temp'], 1)}{unit_symbol}", className="text-center mt-2"),
                html.Small(row["weather"], className="text-center d-block text-muted")
            ])
        ], className="hourlyCards")
        hourly_cards.append(card_data)

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
    map_fig.update_layout(mapbox_style="open-street-map",
                          hoverlabel=dict(
                              bgcolor="rgba(30, 30, 30, 0.9)",  
                              font_color="white",
                              font_size=14,      
                          ))

    layer_urls = {
        "temp-overlay": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "precipitation-overlay": f"https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "pressure-overlay": f"https://tile.openweathermap.org/map/pressure_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "wind-overlay": f"https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}",
        "cloud-overlay": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}"
    }

    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        clicks = {
            "temp-overlay": temp_clicks,
            "precipitation-overlay" :precipitation_clicks,
            "pressure-overlay": pressure_clicks,
            "wind-overlay": wind_clicks,
            "cloud-overlay": cloud_clicks
        }

        if button_id in layer_urls and clicks[button_id] > 0:
            overlay_url = layer_urls[button_id]
            zoom_level = 5

    map_fig.update_layout(mapbox={
        "zoom": zoom_level,
        "layers": [{"sourcetype":"raster","source":[overlay_url],"below":"traces"}] if overlay_url else []
    })

    store_data = {
        "df": df.to_dict("records"),
        "city_info": city_info
    }

    return heading, weather_data, map_fig, hourly_cards, store_data
