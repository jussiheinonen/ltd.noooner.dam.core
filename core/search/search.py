from functions import *
from pprint import pprint
import boto3, json, os

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')

if IS_OFFLINE:
    ddb_client = boto3.client(
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    ddb_client = boto3.client('dynamodb')

def ddb_scan_all(client, table):
    response = client.scan(TableName=table)
    return response

def lambda_handler(event, context):
    params = event['queryStringParameters']['q']
    print(f"Query Parameters {params}")

    #pprint(event)
    return(event)

    #response = mockQueryResponse() # returns a dict

    print(f"Scanning table {INDEX_TABLE}")
    response = ddb_scan_all(ddb_client, INDEX_TABLE)

    pprint(response)
    return response