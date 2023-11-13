import openai
import json
import os, sys
from config import Config

class Query:
    def __init__(self):
        self.model = Config.OPENAI_MODEL
        self.api_key = Config.SECRET_KEY

    def send_query(self, prompt: str):
        raise NotImplementedError("Subclasses must implement this method.")
    
class ChatCompletionJSON(Query):
    def __init__(self, tokens: int):
        super().__init__()
        self.tokens = tokens 

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

        if isinstance(api_response, str):
            try:
                api_response = json.loads(api_response)
                print(api_response)

                locations = [loc['name'] for loc in api_response['locations']]
                relationships = [{'source': rel['source'], 'relation': rel['relation'], 'target': rel['target']} for rel in api_response['relationships']]

                return api_response, locations, relationships
            except json.JSONDecodeError:
                print("THe API response is not valid JSOn.")
        else:
            print("THe API response is already a python Dictionary, no need to parse it.")


class ChatCompletionOther(Query):
    def __init__(self, tokens: int):
        super().__init__()
        self.tokens = tokens 

    def send_query(self, prompt: str):
        openai.api_key = self.api_key
        full_prompt = Config.OTHER_PROMPT
        response = openai.Completion.create(
            engine = self.model,
            prompt = full_prompt,
            temperature = 0.5,
            max_tokens = Config.MAX_TOKENS
        )

        api_response = response.choice[0].text.strip()
        return api_response