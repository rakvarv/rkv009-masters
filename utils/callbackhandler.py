from dash import Input, Output, no_update, html
import pyvis
import json
import os
from config import Config
from utils.graphhandler import KnowledgeGraphCreator
from utils.queryhandler import ChatCompletionJSON




def register_callbacks(app):
    @app.callback(
        Output('graph-div', 'children'),
        [Input('graph-creator', 'n_clicks')]
    )
    def display_graph(n_clicks):
        if n_clicks is None:
            return no_update
        else:
            query = ChatCompletionJSON(200)
            api_response, locations, relationships = query.send_query("yo.")
            print(api_response)
            print(locations)
            print(relationships)

            graph_handler = KnowledgeGraphCreator(locations, relationships)
            pyvis_graph = graph_handler.create_knowledge_graph()

            if os.path.isfile("kg.html"):
                return html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="600px")
            else:
                return html.P("Knowledge Graph Creation Has Failed...")