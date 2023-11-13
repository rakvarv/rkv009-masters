import os 
import rdflib
import kglab
from config import Config


class KnowledgeGraphCreator:
    def __init__(self, locations, relationships):
        self.locations = locations 
        self.relationships = relationships
        self.kg = kglab.KnowledgeGraph()

    def create_knowledge_graph(self):
        if os.path.isfile("master_thesis.ttl"):
            self.kg.load_rdf("master_thesis.ttl")
            print("previous RDF loaded")

        LOC = rdflib.Namespace("http://example.org/locations/")
        REL = rdflib.Namespace("http://example.org/relationships/")

        self.kg.add_ns("loc", LOC)
        self.kg.add_ns("rel", REL)

        # add locations to graph
        for location in self.locations:
            self.kg.add(LOC[location], rdflib.RDF.type, LOC.location)

        # Add relationships to graph:
        for relationship in self.relationships:
            source = LOC[relationship['source']]
            target = LOC[relationship['target']]
            relation = REL[relationship['relation']]
            self.kg.add(source, relation, target)

        try:
            self.kg.save_rdf("master_thesis.ttl")
        except Exception as e:
            print("RDF Failed To Save...")
        
        subgraph = kglab.SubgraphTensor(self.kg)
        graph_style = Config.GRAPH_STYLE
        pyvis_graph = subgraph.build_pyvis_graph(notebook="true", style=graph_style)
        pyvis_graph.force_atlas_2based
        pyvis_graph.show("kg.html")

        return pyvis_graph