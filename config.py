import os 
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = os.getenv("OPENAI_KEY")
    DEBUG = False
    TESTING = False 
    OPENAI_MODEL = 'text-davinci-003'
    JSON_PROMPT = """

    I am an AI model and I have been trained to extract and structure information about locations and their relationships from text and all locations bordering the mentioned locations, including the geospatial relation. The output will be in a valid JSON format using double quotes, not single. Do not specify you are writing the output, only write the JSON.  Here are a few examples:

    Text: "Paris is in France. It is next to Versailles."

    {
      "locations": [
        {"name": "Paris", "type": "Location"},
        {"name": "France", "type": "Location"},
        {"name": "Versailles", "type": "Location"}
      ],
      "relationships": [
        {"source": "Paris", "relation": "isIn", "target": "France"},
        {"source": "Paris", "relation": "isNextTo", "target": "Versailles"}
      ]
    }

    Text: "New York is in the United States. It is next to New Jersey."

    {
      "locations": [
        {"name": "New York", "type": "Location"},
        {"name": "United States", "type": "Location"},
        {"name": "New Jersey", "type": "Location"}
      ],
      "relationships": [
        {"source": "New York", "relation": "isIn", "target": "United States"},
        {"source": "New York", "relation": "isNextTo", "target": "New Jersey"}
      ]
    }

    Now, given the following text, please extract the locations and their geographical relationships and return the output in a valid JSON format:

    Text: \"Stavanger er Vestland, Norge. Mens Bodø er i Nordland.\"

    """
    OTHER_PROMPT = "What is the capital of norway?"
    MAX_TOKENS = 200
    GRAPH_STYLE = {
        "wtm": {
            "color" : "orange",
            "size" : 40
        },
        "ind":{
            "color" : "blue",
            "size" : 30
        }
    }

class ProductionConfig(Config):
    DATABASE_URI = os.environ.get('DATABASE_URI')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True