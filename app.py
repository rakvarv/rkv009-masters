from dash import Dash, dcc, html, Input, Output, callback
import dash
import os, sys
import openai
import json
from config import DevelopmentConfig
from utils.callbackhandler import extract_locations_from_ttl, register_callbacks

app = Dash(__name__)    
app.server.config.from_object(DevelopmentConfig)
app.suppress_callback_exceptions = True

if os.path.isfile("./utils/kg.html"):
    if os.path.isfile("./master_thesis.ttl"):
        ttl_content = "./master_thesis.ttl"
        locations = extract_locations_from_ttl(ttl_content=ttl_content)
        app.layout = html.Div([
            html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="1000px"),
            html.Div(id="graph-div")
        ], id="main-div")
    else:
        app.layout = html.Div([
            html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="1000px"),
            html.Div(id="graph-div"),
        ], id="main-div")
else:
    if os.path.isfile("./master_thesis.ttl"):
        ttl_content = "./master_thesis.ttl"
        locations = extract_locations_from_ttl(ttl_content=ttl_content)
        app.layout = html.Div([
            html.P("No HTML file exists here."),
            html.Button('Submit', id='graph-creator', n_clicks=0),
            html.Div(id="graph-div"),
            dcc.Dropdown(
                id='location-dropdown',
                options=[{'label': loc, 'value': loc} for loc in locations],
                value=locations[0] if locations else None  # Default value or None if no locations
            ),
            html.Button("Confirm Selection", id="confirm-button", n_clicks=0),
            html.Div(id="relationship-output") # Placeholder for relationship visualization
        ], id="main-div")
    else:
        app.layout = html.Div([
            html.P("No HTML file exists here."),
            html.Button('Submit', id='graph-creator', n_clicks=0),
            html.Div(id="graph-div"),
            html.Button("Confirm Selection", id="confirm-button", n_clicks=0),
            html.Div(id="relationship-output") # Placeholder for relationship visualization
        ], id="main-div")

# Activates callbacks to be able to be ran
# Comment out to disable all callbacks from being ran.
register_callbacks(app)

if __name__ == "__main__":
    app.run_server()
