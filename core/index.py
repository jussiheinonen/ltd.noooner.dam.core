import json, sys, os
import urllib.parse
import boto3

print('Loading function')

IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    s3_client = boto3.client(
        's3',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'test',
        aws_secret_access_key = 'test'
    )
else:
    s3_client = boto3.client('s3')


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
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


