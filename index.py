from dash import Input, Output, callback
from utils.query_handler import ChatCompletionJSON
from app import app

# Initiatelize query object
query = ChatCompletionJSON("gpt-3.5-turbo", 100)

# @app.callback(
#     Output('my-output', 'children'),
#     Input('my-input', 'value')
# )
# def update_output_div(input_value):
#     response = query.send_query()

#     return response