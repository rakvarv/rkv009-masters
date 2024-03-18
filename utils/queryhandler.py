import openai
import json
import os, sys
from config import Config
from openai import OpenAI

# Define a base class for sending queries to the OpenAI API
class Query:
    # Initialize the class with the model and API key
    def __init__(self):
        self.model = Config.OPENAI_MODEL
        self.api_key = Config.SECRET_KEY

    # Define a method for sending a query
    # This method is not implemented in this base class and must be implemented in any subclasses
    def send_query(self, prompt: str):
        raise NotImplementedError("Subclasses must implement this method.")
    
# Define a subclass for sending chat completion queries that return JSON responses
class ChatCompletionJSON(Query):
    # Initialize the class with the number of tokens
    def __init__(self, tokens: int):
        super().__init__()
        self.tokens = tokens 

    # Implement the send_query method for this subclass
    def send_query(self, prompt: str):

        #openai.api_key = self.api_key
        openai.api_key = "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"
        client = OpenAI(api_key="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")
        response = client.chat.completions.create(
            model = "gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "I am an AI model and I have been trained to extract and structure information about locations and their geo spatial relationships from texts and all locations bordering the mentioned locations. The output will be in a valid JSON format using double quotes, not single. Do not specify you are writing the output, only write the JSON. If the locations include whitespaces, make the location in camel case writing. Here are a few examples:"},
                {"role": "user", "content": "Text: Paris is in France. It is next to Versailles."},
                {"role": "assistant", "content": '{"locations": [{"name": "Paris", "type": "Location"}, {"name": "France", "type": "Location"}, {"name": "Versailles", "type": "Location"}], "relationships": [{"source": "Paris", "relation": "isIn", "target": "France"}, {"source": "Paris", "relation": "isNextTo", "target": "Versailles"}]}'},
                {"role": "user", "content": "Text: New York is in the United States. It is next to New Jersey."},
                {"role": "assistant", "content": '{"locations": [{"name": "New York", "type": "Location"}, {"name": "United States", "type": "Location"}, {"name": "New Jersey", "type": "Location"}], "relationships": [{"source": "New York", "relation": "isIn", "target": "United States"}, {"source": "New York", "relation": "isNextTo", "target": "New Jersey"}]}'},
                {"role": "user", "content": f"Now, given the following text, please extract the locations and their geographical relationships and return the output in a valid JSON output format, and do it to anything that remotely resemble a geo location: Text: {prompt}"}
            ],
            temperature = 0.5,
            max_tokens = Config.MAX_TOKENS
        )
        api_response = response.choices[0].message.content
        print(api_response)

        # Check if the API response is a string
        if isinstance(api_response, str):
            try:
                # Try to parse the string as JSON
                api_response = json.loads(api_response)

                # Extract the locations and relationships from the API response
                #locations = [loc['name'] for loc in api_response['locations']]
                #relationships = [{'source': rel['source'], 'relation': rel['relation'], 'target': rel['target']} for rel in api_response['relationships']]

                if 'locations' in api_response:
                    locations = [loc['name'] for loc in api_response['locations']]
                else:
                    locations = []  # or any appropriate default value

                relationships = []
                for rel in api_response.get('relationships', []):
                    try:
                        relationships.append({
                            'source': rel['source'],
                            'relation': rel['relation'],
                            'target': rel['target']
                        })
                    except KeyError as e:
                        # Handle the missing key: log it, append a placeholder, etc.
                        print(f"Missing key {e} in relationship: {rel}")

                print(locations)
                print(relationships)

                return api_response, locations, relationships
            except json.JSONDecodeError:
                print("The API response is not valid JSON.")
        else:
            print("The API response is already a python Dictionary, no need to parse it.")

# Define a subclass for sending chat completion queries that return other types of responses
class ChatCompletionGPT20(Query):
    # Initialize the class with the number of tokens
    def __init__(self, tokens: int):
        super().__init__()
        self.tokens = tokens 

    # Implement the send_query method for this subclass
    def send_query(self, prompt: str):
        openai.api_key = self.api_key
        client = OpenAI()
        response = client.chat.completions.create(
            model = self.model,
            messages=[
                {"role": "system", "content": "I am an AI model and I have been trained to extract and structure information about locations and their geo spatial relationships in Vestland, Norway from text and all locations bordering the mentioned locations. The output will be in a valid JSON format using double quotes, not single. Do not specify you are writing the output, only write the JSON.  Here are a few examples:"},
                {"role": "user", "content": "Text: Paris is in France. It is next to Versailles."},
                {"role": "assistant", "content": '{"locations": [{"name": "Paris", "type": "Location"}, {"name": "France", "type": "Location"}, {"name": "Versailles", "type": "Location"}], "relationships": [{"source": "Paris", "relation": "isIn", "target": "France"}, {"source": "Paris", "relation": "isNextTo", "target": "Versailles"}]}'},
                {"role": "user", "content": "Text: New York is in the United States. It is next to New Jersey."},
                {"role": "assistant", "content": '{"locations": [{"name": "New York", "type": "Location"}, {"name": "United States", "type": "Location"}, {"name": "New Jersey", "type": "Location"}], "relationships": [{"source": "New York", "relation": "isIn", "target": "United States"}, {"source": "New York", "relation": "isNextTo", "target": "New Jersey"}]}'},
                {"role": "user", "content": "Now, given the following text, please extract the locations and their geographical relationships and return the output in a valid JSON format: {newsContent}"}
            ],
            temperature = 0.5,
            max_tokens = Config.MAX_TOKENS
        )

        # Extract the API response
        api_response = response.choices[0].message.content
        return api_response
