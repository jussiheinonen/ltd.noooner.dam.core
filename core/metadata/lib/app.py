import boto3, os
from botocore.exceptions import ClientError
from pprint import pprint

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')

if IS_OFFLINE:
    ddb_client = boto3.resource(
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    ddb_client = boto3.resource('dynamodb')

def get_metadata(id, ddb_client, ddb_table):
    
    table = ddb_client.Table(ddb_table)

    try:
        response = table.get_item(Key={'id': id})
    except ClientError as e:
        return e.response['Error']['Message']

    try: 
        return response['Item']
    except:
        not_found_object = { "response": "Not found" }
        return not_found_object


def lambda_handler(event, context):
    id = event['queryStringParameters']['id']
    print(f"Getting metadata for image ID {id}")
    response = get_metadata(id, ddb_client, INDEX_TABLE)

    return response