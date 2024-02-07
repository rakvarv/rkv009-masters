import os 
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = os.getenv("OPENAI_API_KEY")
    DEBUG = False
    TESTING = False 
    OPENAI_MODEL = 'gpt-4-1106-preview'
    GPT3_MODEL = "gpt-3.5-turbo-1106"
    JSON_PROMPT = "{newsContent}"

    OTHER_PROMPT = "What is the capital of norway?"
    MAX_TOKENS = 4000
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
