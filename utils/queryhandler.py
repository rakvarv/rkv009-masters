import openai
import json
import os, sys
from config import Config

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
        openai.api_key = self.api_key
        full_prompt = Config.JSON_PROMPT
        response = openai.Completion.create(
            engine = self.model,
            prompt = full_prompt,
            temperature = 0.5,
            max_tokens = Config.MAX_TOKENS
        )
        api_response = response.choices[0].text.strip()

        # Check if the API response is a string
        if isinstance(api_response, str):
            try:
                # Try to parse the string as JSON
                api_response = json.loads(api_response)
                print(api_response)

                # Extract the locations and relationships from the API response
                locations = [loc['name'] for loc in api_response['locations']]
                relationships = [{'source': rel['source'], 'relation': rel['relation'], 'target': rel['target']} for rel in api_response['relationships']]

                return api_response, locations, relationships
            except json.JSONDecodeError:
                print("The API response is not valid JSON.")
        else:
            print("The API response is already a python Dictionary, no need to parse it.")

# Define a subclass for sending chat completion queries that return other types of responses
class ChatCompletionOther(Query):
    # Initialize the class with the number of tokens
    def __init__(self, tokens: int):
        super().__init__()
        self.tokens = tokens 

    # Implement the send_query method for this subclass
    def send_query(self, prompt: str):
        openai.api_key = self.api_key
        full_prompt = Config.OTHER_PROMPT
        response = openai.Completion.create(
            engine = self.model,
            prompt = full_prompt,
            temperature = 0.5,
            max_tokens = Config.MAX_TOKENS
        )

        # Extract the API response
        api_response = response.choices[0].text.strip()
        return api_response
