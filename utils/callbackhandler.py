from dash import Input, Output, no_update, html
import pyvis
import json, os
import pandas as pd
from config import Config
from utils.graphhandler import KnowledgeGraphCreator
from utils.queryhandler import ChatCompletionJSON
import rdflib
import dash 

# Define a function to register callbacks for the Dash app
def register_callbacks(app):
    # Define a callback for displaying the graph
    @app.callback(
        Output('graph-div', 'children'),  # The output is the children of the 'graph-div' element
        [Input('graph-creator', 'n_clicks')],  # The input is the number of clicks on the 'graph-creator' element
        prevent_initial_callback=True
    )
    def display_graph(n_clicks):
        # If the button hasn't been clicked, don't update the graph
        new_locations = []
        new_relationships = []
        news_db = pd.read_csv("data\\news_db.csv") # CSV with all the news texts.
        news_db = news_db.replace('-', '', regex=True)
        if n_clicks > 2:
            return no_update
        else:
            for i, row in news_db.iterrows():
                print(row["news_content"])

                # Create a query object with 200 tokens
                query = ChatCompletionJSON(4000)
                # Send a query to the OpenAI API
                api_response = {"locations": [], "relationships": []}
                if api_response:
                    api_response, locations, relationships = query.send_query(row["news_content"])

                    for location in locations:
                        if location not in new_locations:
                            new_locations.append(location)
                    for relationship in relationships:
                        if relationship not in new_relationships:
                            new_relationships.append(relationship)
                else:
                    print("An error occured with send_query.")
                    continue

            # Create a graph handler object with the locations and relationships from the API response
            graph_handler = KnowledgeGraphCreator(new_locations, new_relationships)
            # Create a knowledge graph
            pyvis_graph = graph_handler.create_knowledge_graph()

            # If the graph was successfully created, display it in an iframe
            if os.path.isfile("kg.html"):
                return html.Iframe(srcDoc=open("kg.html", "r").read(), width="100%", height="600px")
            else:
                # If the graph creation failed, display an error message
                return html.P("Knowledge Graph Creation Has Failed...")
            
    @app.callback(
        Output('relationship-output', 'children'),
        [Input('confirm-button', 'n_clicks')],
        [dash.dependencies.State('location-dropdown', 'value')]
    )
    def display_relationships(n_clicks, selected_location):
        if n_clicks > 0:
            ttl_content = "./master_thesis.ttl"
            with open(ttl_content, 'r') as file:
                ttl_content = file.read()
            relationships = get_relationships_for_location(selected_location, ttl_content)
            # Format for display
            formatted_relationships = [
                html.Div(f"{rel_type} - {loc}") for rel_type, loc in relationships
            ]
            return html.Div(formatted_relationships)
        return ''

# Helper function for extracting locations from TTL file.
def extract_locations_from_ttl(ttl_content):
    with open(ttl_content, 'r') as file:
        ttl_content = file.read()
    g = rdflib.Graph()
    g.parse(data=ttl_content, format="turtle")

    locations = set()
    for s, p, o in g:
        if str(s).startswith("http://example.org/locations/"):
            location = str(s).split('/')[-1]
            locations.add(location)

    return list(locations)

def get_relationships_for_location(location, ttl_content):
    g = rdflib.Graph()
    g.parse(data=ttl_content, format="turtle")

    # Adjusted SPARQL query to get both relationship type and target location
    query = f"""
    PREFIX loc: <http://example.org/locations/>
    PREFIX rel: <http://example.org/relationships/>

    SELECT ?relationshipType ?otherLocation WHERE {{
        loc:{location} ?relationship ?otherLocation .
        BIND(STRAFTER(STR(?relationship), "http://example.org/relationships/") AS ?relationshipType)
    }}
    """

    results = g.query(query)
    return [(str(result[0]), str(result[1]).split('/')[-1]) for result in results]

