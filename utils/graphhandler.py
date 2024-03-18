import os
import rdflib
import kglab
from config import Config
from urllib.parse import quote

# Define a class for creating a knowledge graph
class KnowledgeGraphCreator:
    # Initialize the class with locations and relationships
    def __init__(self, locations, relationships):
        self.locations = locations
        self.relationships = relationships
        self.kg = kglab.KnowledgeGraph()  # Create an instance of a knowledge graph

    # Define a method for creating the knowledge graph
    def create_knowledge_graph(self):
        # Check if the turtle file exists
        if os.path.isfile("master_thesis.ttl"):
            self.kg.load_rdf("master_thesis.ttl")  # Load the existing graph
            print("previous RDF loaded")

        # Define the namespaces
        LOC = rdflib.Namespace("http://example.org/locations/")
        REL = rdflib.Namespace("http://example.org/relationships/")

        # Add the namespaces to the knowledge graph
        self.kg.add_ns("loc", LOC)
        self.kg.add_ns("rel", REL)

        # Add locations to the graph
        for location in self.locations:
            if isinstance(location, dict) and 'name' in location:
                encoded_location_name = quote(location['name'])  # Encode location name
                location_uri = LOC[encoded_location_name]
                print("RDF: ", (location_uri, rdflib.RDF.type, LOC.Location))

                # Check if the location already exists in the graph
                if (location_uri, rdflib.RDF.type, LOC.location) not in self.kg.rdf_graph():
                    self.kg.add(location_uri, rdflib.RDF.type, LOC.location)  # Add the location if it doesn't exist

        # Add relationships to the graph
        for relationship in self.relationships:
            print("Source:", relationship['source'])
            print("Target:", relationship['target'])
            source = LOC[quote(relationship['source'])]  # Encode source location name
            target = LOC[quote(relationship['target'])]  # Encode target location name
            relation = REL[relationship['relation']]

            # Checks if the relationship already exists in the graph
            if (source, relation, target) not in self.kg.rdf_graph():
                self.kg.add(source, relation, target)  # Add the relationship if it doesn't exist

        # Try to save the graph
        try:
            self.kg.save_rdf("master_thesis.ttl")
        except Exception as e:
            print("RDF Failed To Save...")

        # Create a subgraph tensor
        subgraph = kglab.SubgraphTensor(self.kg)
        graph_style = Config.GRAPH_STYLE
        # Build a PyVis graph from the subgraph tensor
        pyvis_graph = subgraph.build_pyvis_graph(notebook="true", style=graph_style)
        pyvis_graph.force_atlas_2based
        # Show the graph
        pyvis_graph.show("kg.html")

        # Return the PyVis graph
        return pyvis_graph
