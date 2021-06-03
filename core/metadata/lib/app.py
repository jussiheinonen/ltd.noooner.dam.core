import boto3, os, json, decimal
from botocore.exceptions import ClientError
from pprint import pprint
from boto3.dynamodb.types import TypeDeserializer

deserializer = TypeDeserializer()

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')

if IS_OFFLINE:
    #ddb_client = boto3.resource(
    ddb_client = boto3.client(        
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    #ddb_client = boto3.resource('dynamodb')
    ddb_client = boto3.client('dynamodb')

def get_metadata_ddb_client(id, ddb_client, ddb_table):
    response = ddb_client.get_item(
        TableName=ddb_table,
        Key={ 
            'id': {
                'S': id
            }
         })

    deserialised = {k: deserializer.deserialize(v) for k, v in response.get("Item").items()}
    
    #for key, value in deserialised.items():
    #    print('Key ' + key + ' is type of ' + str(type(value)))

    
    #return None
    return json.dumps(deserialised, cls=SetEncoder)

def get_metadata_ddb_table(id, ddb_client, ddb_table):
    
    table = ddb_client.Table(ddb_table)

    try:
        print('Calling table.get_item')
        response = table.get_item(Key={'id': id})
    except ClientError as e:
        print('OOOPS! Failed calling table.get_item')
        return e.response['Error']['Message']

    try:
        print('Returning found_object response to lambda_handler')
        return json.dumps(response['Item'], cls=SetEncoder)
    except:
        not_found_object = { 'response': 'Not found' }
        print('Returning not_found_object response to lambda_handler')
        return not_found_object


def lambda_handler(event, context):

    id = event['queryStringParameters']['id']
    print(f"Getting metadata for image ID {id}")
    response = get_metadata_ddb_client(id, ddb_client, INDEX_TABLE)
    return response