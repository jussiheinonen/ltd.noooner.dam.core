from functions import *
from pprint import pprint
import json

def lambda_handler(event, context):
    response = mockQueryResponse() # returns a dict
    pprint(response)
    return response