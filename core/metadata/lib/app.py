import boto3, os, json, decimal
from botocore.exceptions import ClientError
from pprint import pprint
from functions import *
from copy import Error

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
    ddb_client = boto3.resource(
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    ddb_client = boto3.resource('dynamodb')

def get_metadata_ddb_table(id, ddb_client, ddb_table):
    
    table = ddb_client.Table(ddb_table)

    try:
        print(f'Calling table.get_item for key {id}')
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

    ddb_key = event['queryStringParameters']['id']
    print(f"Getting metadata for image ID {ddb_key}")
    http_method = event['requestContext']['http']['method']
    print(f"HTTP method is {http_method}")

    if http_method == 'GET':
        '''
        ============
        CURL EXAMPLE
        ============
        https://5xa8nazic2.execute-api.eu-west-1.amazonaws.com/metadata?id=520a1db1df5614bc9f8d89ab42a32561
        '''
        response = get_metadata_ddb_table(ddb_key, ddb_client, INDEX_TABLE)

    elif http_method == 'PUT':
        '''
        ============
        CURL EXAMPLE
        ============
        curl -X 'PUT' \
        'https://5xa8nazic2.execute-api.eu-west-1.amazonaws.com/metadata?id=520a1db1df5614bc9f8d89ab42a32561' \
        -d '{ "n_search": ["train", "timetable"] }' \
        -H "Content-Type: application/json" 
        '''

        if ddb_key_exists(ddb_key, ddb_client, INDEX_TABLE):          
            try:
                payload = json.loads(event['body'])
                update_epoch = str(event['requestContext']['timeEpoch'])
                updated_datetime = str(event['requestContext']['time'])
                payload['update_epoch'] = update_epoch
                payload['update_datetime'] = updated_datetime
                print('Attempting to update data ' + str(payload))
                
                response = ddb_update_item(ddb_key, ddb_client, INDEX_TABLE, payload)
                
            except Error as e:
                print('Failed to find event body part ' + e )
                pprint(event)
                response = { "error": "failed to get event body part"}
        else:
            message = "No item " + ddb_key
            response = { "response" :  message }
            

    elif http_method == 'POST':
        response = unimplementedHttpMethod('POST')
    return response