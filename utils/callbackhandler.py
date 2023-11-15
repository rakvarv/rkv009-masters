from dash import Input, Output, no_update, html
import pyvis
import json
import os
from config import Config
from utils.graphhandler import KnowledgeGraphCreator
from utils.queryhandler import ChatCompletionJSON

# Define a function to register callbacks for the Dash app
def register_callbacks(app):
    # Define a callback for displaying the graph
    @app.callback(
        Output('graph-div', 'children'),  # The output is the children of the 'graph-div' element
        [Input('graph-creator', 'n_clicks')]  # The input is the number of clicks on the 'graph-creator' element
    )
    def display_graph(n_clicks):
        # If the button hasn't been clicked, don't update the graph
        if n_clicks is None:
            return no_update
        else:
            # Create a query object with 200 tokens
            query = ChatCompletionJSON(200)
            # Send a query to the OpenAI API
            api_response, locations, relationships = query.send_query("yo.")
            print(api_response)
            print(locations)
            print(relationships)

            # Create a graph handler object with the locations and relationships from the API response
            graph_handler = KnowledgeGraphCreator(locations, relationships)
            # Create a knowledge graph
            pyvis_graph = graph_handler.create_knowledge_graph()

            # If the graph was successfully created, display it in an iframe
            if os.path.isfile("kg.html"):
                return html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="600px")
            else:
                # If the graph creation failed, display an error message
                return html.P("Knowledge Graph Creation Has Failed...")
