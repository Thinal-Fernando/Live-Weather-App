import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from utils import get_weather
import pandas as pd

dash.register_page(__name__, path='/stats', name='Stats')

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Weather Statistics"),
            dbc.Button("☰ Menu", id="menu-button", color="dark", className="mb-3"),
            
            dbc.Offcanvas([
                html.H5("Options", className="mb-3"),
                html.Hr(),
                dbc.Button("Home", href="/", id="btn-clouds", color="secondary", className="mb-2", n_clicks=0),  
                dbc.Button("Details", href="/stats",  id="btn-rain", color="primary", className="mb-2",  n_clicks=0),  
            ], id="sidebar-stats", placement="start", is_open=False),

            
           
            
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Slider(id="temp-slider", min=0, max=50, step=1, value=50, marks={0:"0°C",10:"10°C",20:"20°C",30:"30°C",40:"40°C",50:"50°C"}),
                    dcc.Graph(id="temp-graph"),
                ])
            ])
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                     dcc.Graph(id="humidity-graph"),
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="wind-graph"),
                ])
            ])
        ], width=6),

    ]),
], fluid=True)

@dash.callback(
    Output("sidebar-stats", "is_open"),
    Input("menu-button", "n_clicks"),
    State("sidebar-stats", "is_open"),
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open


@dash.callback(
    Output("temp-graph", "figure"),
    Output("humidity-graph", "figure"),
    Output("wind-graph", "figure"),
    Input("shared-city-data", "data"),
    Input("temp-slider", "value"),

)
def update_stats(data, max_temp):
    if not data or "df" not in data or "city_info" not in data:
        return px.scatter(), px.scatter(), px.scatter()

    
    df = pd.DataFrame(data["df"])
    city_info = data["city_info"]

    temp_fig = px.histogram(df[df["temp"] <= max_temp], x="temp", nbins=10, title=f"Temperature <= {max_temp}")
    humidity_fig = px.line(df, x="time", y="humidity", title="Humidity Over Time")
    wind_fig = px.line(df, x="time", y="wind", title="Wind Speed Over Time")

    return temp_fig, humidity_fig, wind_fig
