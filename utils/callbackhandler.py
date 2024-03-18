from dash import Input, Output, no_update, html
import pyvis
import json, os
import pandas as pd
from config import Config
from utils.graphhandler import KnowledgeGraphCreator
from utils.queryhandler import ChatCompletionJSON
import rdflib
import dash

def save_json(json_object, file_path):
    # Extract the directory path from the file path
    directory = os.path.dirname(file_path)
    
    # If the directory doesn't exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        # Open the file in append mode if it exists, otherwise create a new file
        with open(file_path, 'a+' if os.path.exists(file_path) else 'w') as json_file:
            # If file is not empty, move cursor to the end
            json_file.seek(0, 2)
            if json_file.tell() > 0:
                json_file.write(',')  # Add a comma to separate objects
            
            # Dump JSON object to file
            json.dump(json_object, json_file, indent=4)
            json_file.write('\n')  # Add a newline after the object
        print("JSON appended successfully to:", file_path)
    except Exception as e:
        print("Error occurred while saving JSON:", e)

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

                # Check if "predicted" column exists, if not, create it
                if "predicted" not in news_db.columns:
                    news_db["predicted"] = ""

                # Add the api_response to the "predicted" column in the DataFrame
                news_db.at[i, "predicted"] = api_response
                print(news_db.columns)
                news_db.to_csv("C:\\Users\\rakva\\Documents\\rkv009-masters-main\\rkv009-masters-main\\testing.csv")
                    
            try:
                save_json(api_response, "C:\\Users\\rakva\\Documents\\api_json\\data.json")
            except Exception as e:
                print(f"Error occured while saving api response as JSON: {e}")

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

def calculate_accuracy(row):
    """
    Calculate accuracy based on predicted and actual values in a DataFrame row.

    Paramters:
        row (Pandas.Series): DataFrame row containing "predicted" and "actual" column
    
    Returns:
        float: Accuracy score,
    """
    try:
        predicted = json.loads(row["predicted"])
        actual = json.loads(row["actual"])

        #Initialize accuracy and accuracy components
        accuracy = 0
        location_accuracy = 0
        relationship_accuracy = 0

        # Compare number of locations
        predicted_locations = len(predicted.get("locations", []))
        actual_locations = len(actual.get("locations", []))
        if predicted_locations == actual_locations:
            location_accuracy = 1
        elif predicted_locations > actual_locations:
            location_accuracy = actual_locations / predicted_locations
        else:
            location_accuracy = predicted_locations / actual_locations
        
        # Compare relationships
        predicted_relationships = set([(rel['from'], rel['relation'], rel['target']) for rel in predicted.get('relationships', [])])
        actual_relationships = set([(rel['from'], rel['relation'], rel['target']) for rel in actual.get('relationships', [])])
        common_relationships = predicted_relationships.intersection(actual_relationships)
        relationship_accuracy = len(common_relationships) / max(len(predicted_relationships), len(actual_relationships))

        # Combine location accuracy and relationship accuracy
        accuracy = (location_accuracy + relationship_accuracy) / 2

        return accuracy
    except Exception as e:
        print(f"Error occured while calculating accuracy: {e}")


def evaluate_accuracy(data):
    """
    Evaluate accuracy of predicted values compared to actual values.

    Parameters:
        data (pandas.DataFrame): DataFrame containing 'predicted' and 'actual' columns.

    Returns:
        float: Overall accuracy score.
    """
    total_accuracy = data.apply(calculate_accuracy, axis=1).sum()
    overall_accuracy = total_accuracy / len(data)
    return overall_accuracy


