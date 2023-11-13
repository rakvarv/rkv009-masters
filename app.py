from dash import Dash, dcc, html, Input, Output, callback
import os, sys
import openai
import json
from config import DevelopmentConfig
import utils.callbackhandler as ch

app = Dash(__name__)    
app.server.config.from_object(DevelopmentConfig)
app.suppress_callback_exceptions = True

if os.path.isfile("./utils/kg.html"):
    app.layout = html.Div([
        html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="600px")
    ], id="graph-div")
else:
    app.layout = html.Div([
        html.P("No HTML file exists here."),
        html.Button('Submit', id='graph-creator', n_clicks=0)
    ], id="graph-div")

# Activates callbacks to be able to be ran
# Comment out to disable all callbacks from being ran.
ch.register_callbacks(app)

if __name__ == "__main__":
    app.run_server()