import json, sys, os
import urllib.parse
import boto3
from iptcinfo3 import IPTCInfo
from functions import *

print('Loading function')

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ['INDEX_TABLE']

if IS_OFFLINE:
    s3_client = boto3.client(
        's3',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'test',
        aws_secret_access_key = 'test'
    )

    ddb_client = boto3.client(
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )

else:
    s3_client = boto3.client('s3')
    ddb_client = boto3.client('dynamodb')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print('Bucket is ' + str(bucket) + ', Key is ' + str(key))
    #sys.exit(0)
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        response_body = response['Body'].read() # StreamingBody to bytes
        print('Response Body size ' + str(len(response_body)) + ' bytes')
        #return response['ContentType']

        with open("tmp.jpg", "wb") as binary_file: #Write bytes to file so that IPTCInfo class can access it
            binary_file.write(response_body)

        info = IPTCInfo("tmp.jpg", force=True, inp_charset='UTF-8') # creates iptcinfo3.IPTCInfo object
        fields = [
            'keywords',
            'headline',
            'by-line',
            'by-line title',
            'caption/abstract',
            'source',
            'copyright notice',
            'special instructions',
            'city',
            'country/primary location code',
            'country/primary location name',
            'writer/editor',
            'object name',
            'date created',
            'time created',

            ]
        dict_info = {
            'md5': md5sum(response_body),
            'original_filename': key
        }
        for field in fields:
            try:
                if info[field]:
                    dict_info[field] = info[field]
            except KeyError:
                print('Failed to find key ' + field)

        if len(dict_info) == 0:
            print('No IPTC data found')
        else:
            # About DDB schema https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SampleData.html
            print('Size fo the object dict_info: ' + str(sys.getsizeof(dict_info)) + " bytes")
            print('Dictionary object dict_info has ' + str(len(dict_info)) + " items")
            writeDictionaryToDDB(dict_info, INDEX_TABLE, ddb_client)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


