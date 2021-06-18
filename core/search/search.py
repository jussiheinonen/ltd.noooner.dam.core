from functions import *
from pprint import pprint
import boto3, json, os, time, re

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')
PRESIGN_ENDPOINT_URL = os.environ.get('PRESIGN_ENDPOINT_URL')
METADATA_ENDPOINT_URL = os.environ.get('METADATA_ENDPOINT_URL')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET')
PLACEHOLDER_THUMBNAIL_URL = 'https://s3-eu-west-1.amazonaws.com/' + THUMBNAIL_BUCKET + '/00000000000000000000000000000000.jpg'

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
    
    projection_ex='id, headline,original_filename, upload_time, thumbnail_url'
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

def get_metadata(item):
    '''
    example_input = {
        'upload_time': {
            'N': '1619604041'
            }, '
        original_filename': {
            'S': '2020-12-07T142510Z_33248525_RC2EIK97VAWP_RTRMADP_3_SOCCER-AFCCHAMPIONS-YOK-SUW.JPG'
            }, 
        'id': {
            'S': '6dafa7dc8b7825827f20ec10fbab2213'
            }, 
        'headline': {
            'S': 'AFC Champions League - Round of 16 - Yokohama F Marinos v Suwon Bluewings'
            }
        }

    example_output = {
        "get_download_url": get_download_url,
        "headline": headline,
        "upload_time": upload_time
    }
    '''
    metadata_dict = {}

    try:
        headline = item['headline']['S']
    except:
        headline = "N/A"
    org_file = item['original_filename']['S']
    epoch_upload_time = int(item['upload_time']['N'])
    upload_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_upload_time))
    
    # Workout thumbnail url
    try: 
        thumbnail_url =  item['thumbnail_url']['S']
        #print('thumbnail_url in metadata')
    except:
        thumbnail_url = PLACEHOLDER_THUMBNAIL_URL
        #print('thumbnail_url not in metadata, using placeholder')
    
    # Construct Presign URL for object download
    if PRESIGN_ENDPOINT_URL:
        get_download_url = PRESIGN_ENDPOINT_URL + '?filename=' + org_file + '&action=get_object'
    else:
        print('OOOPS! Unable to construct Presign URL for an object. PRESIGN_ENDPOINT_URL unset.')
        get_download_url = '///UNKONWN_PRESIGN_ENDPOINT_URL' + '?filename=' + org_file + '&action=get_object'

    # Constructing metadata URL for full object metadata
    if METADATA_ENDPOINT_URL:
        metadata_url = METADATA_ENDPOINT_URL + '?id=' + item['id']['S']
    else:
        message = 'OOOPS! Unable to construct Metadata URL for an object. METADATA_ENDPOINT_URL unset.'
        print(message)
        metadata_url = message

    metadata_dict = {
        "get_download_url": get_download_url,
        "headline": headline,
        "upload_time": upload_time,
        "metadata_url": metadata_url,
        "thumbnail_url": thumbnail_url

    }

    return(metadata_dict)

def find_ids_per_keyword(results):
    '''
    Extract ids from results and appends them in to dictionary using id as key and list of keywords as value
    For each item under Items key this function calls get_metadata function that extracts remaining metadata
    At the end 2 dictionaries are merged into one and returned

    example_input = {
        'champions': {
            'Count': 12,
            'Items': [
                {
                    'headline': {
                        'S': 'AFC Champions League - Round of '
                                            '16 - Yokohama F Marinos v Suwon '
                                            'Bluewings'
                                            },
                        'id': {
                            'S': '2cbacbd98d286e1ca44299fe93de5c67'
                            },
                        'original_filename': {
                            'S': '2020-12-07T142534Z_188824836_RC2EIK9EXWOU_RTRMADP_3_SOCCER-AFCCHAMPIONS-YOK-SUW.JPG'
                            },
                        'upload_time': {
                            'N': '1619604044'
                            }
                        },

    example_output = {
        '00311825c1adeb60ffff79d7e8a6ee88': {
            'get_download_url': 'https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign?filename=shutterstock_editorial_Shakhtar_Donetsk_vs_Real_Madrid_11088586O.jpg&action=get_object',
            'headline': 'Shakhtar Donetsk vs Real '
                        'Madrid, Kiev, Ukraine - 01 '
                        'Dec 2020',
            'matching_keywords': ['real',
                                  'madrid',
                                  'champions'],
            'relevance': 3,
            'upload_time': '2021-04-28 10:01:02'
            }
        
    '''
    id_to_keyword = {} # Dictionary using id as a key
    id_to_metadata = {}
    
    for key, value in results.items():
        for item in value['Items']:
            id = item['id']['S']
            id_to_keyword.setdefault(id, []).append(key) # Solution provided by Paul Panzer in https://stackoverflow.com/questions/43060655/update-values-of-a-list-of-dictionaries-in-python
            id_to_metadata[id] = get_metadata(item)
    
    # Merge id_to_metadata and id_to_keyword
    for id, keywords in id_to_keyword.items():
        id_to_metadata[id].update(matching_keywords=keywords, relevance=len(id_to_keyword[id]))

    return id_to_metadata



def lambda_handler(event, context):
    params = event['queryStringParameters']['q']
    print(f"Query Parameters {params}")
    lst_params = re.split("[+ ]", params)
    print('Number of params ' + str(len(lst_params)))

    response={} 
    
    for word in lst_params:
        print(f"Scanning table {INDEX_TABLE} for keyword {word}")
        if lst_params[0] == 'all': # query all with q=all
            response['all'] = ddb_scan_all(ddb_client, INDEX_TABLE)
        else:
            response[word] = ddb_scan_a_word_in_field(ddb_client, INDEX_TABLE, word.lower(), 'n_search')
    
    results_json = find_ids_per_keyword(response)
       
    return results_json

