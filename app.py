import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Weather Dashboard", className="text-center my-3"),
            html.Hr(),
            html.Div(
                [dcc.Link(page["name"], href=page["path"], className="me-3") 
                 for page in dash.page_registry.values()]
            ),
            html.Hr(),
            dash.page_container
        ])
    ])
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
