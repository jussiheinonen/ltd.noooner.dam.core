from functions import *
from pprint import pprint
import boto3, json, os, time, requests

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')
PRESIGN_ENDPOINT_URL = os.environ.get('PRESIGN_ENDPOINT_URL')

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

def ddb_scan_a_word_in_field(client, table, word, field):
    '''
    INPUT PARAMS
    client: DynamoDB client object
    table: name of the table to scan
    word: a keyword to search for in field, eg. mardrid
    field: Field in DynamoDB Item to search against
    '''
    projection_ex='id, n_search, headline,original_filename, upload_time'
    filter_ex='contains(' + field + ',:key)'
    expression_at_val={
                    ":key":{
                        "S": word
                    }
                }    

    response = client.scan(
        TableName=table,
        ProjectionExpression=projection_ex,
        FilterExpression=filter_ex,
        ExpressionAttributeValues=expression_at_val
        )
    return response

def getDownloadUrl(filename):
    url = PRESIGN_ENDPOINT_URL
    payload = {
        "method": "get_object",
        "filename": filename
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data = json.dumps(payload), headers=headers)
        return response.text
    except:
        return False


def lambda_handler(event, context):
    params = event['queryStringParameters']['q']
    print(f"Query Parameters {params}")
    lst_params = []
    lst_params = params.split('+')
    print('Number of params ' + str(len(lst_params)))

    print(f"Scanning table {INDEX_TABLE}")
    if lst_params[0] == 'all': # query all with q=all
        response = ddb_scan_all(ddb_client, INDEX_TABLE)
    else:
        response = ddb_scan_a_word_in_field(ddb_client, INDEX_TABLE, lst_params[0].lower(), 'n_search')

    i = 0
    results_lst = [] # list of dictionary items
    results_json = {}
    for item in response['Items']:
        #pprint(item)
        try:
            headline = item['headline']
        except:
            headline = {
                "S": "N/A"
            }
        org_file = item['original_filename']
        epoch_upload_time = item['upload_time']
        epoch_upload_time = int(epoch_upload_time['N'])
        upload_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_upload_time))

        if PRESIGN_ENDPOINT_URL:
            #download_url = getDownloadUrl(org_file['S'])
            get_download_url = PRESIGN_ENDPOINT_URL + '?filename=' + org_file['S'] + '&action=get_object'
            dict_response = {
                "get_download_url": get_download_url,
                "headline": headline['S'],
                "upload_time": upload_time

            }
            results_json[i] = dict_response
            #pprint(results_json)

        else:
            print('Image' + str(i) + ': ' + org_file['S'] + ', with headline: ' + headline['S'] + ', uploaded at: ' + upload_time)
        i += 1

    
    print('NUMBER OF SEARCH RESULTS: ' + str(len(response['Items'])))
    return results_json