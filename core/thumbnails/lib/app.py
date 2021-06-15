from copy import Error
import json, boto3, os, time, requests
from pprint import pprint
from functions import *
from PIL import Image
import urllib.parse

IS_OFFLINE = os.environ.get('IS_OFFLINE')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET')
METADATA_ENDPOINT_URL = os.environ.get('METADATA_ENDPOINT_URL')
THUMBAIL_DIMENSIONS = os.environ.get('THUMBNAIL_DIMENSIONS') # Environment variable syntax THUMBAIL_DIMENSIONS="480,480"
thumbnail_dimensions_defaults = 360,240
thumbnail_bucket_url_base = "https://s3-eu-west-1.amazonaws.com/ltd.noooner.dam.core.thumbnail.ltd-noooner-thumbdev/"

if not THUMBAIL_DIMENSIONS:
    print(f'No environment variable THUMBNAIL_DIMENSIONS. Using default {thumbnail_dimensions_defaults}')
    THUMBAIL_DIMENSIONS = thumbnail_dimensions_defaults
else:
    try:
        lst_dimensions = THUMBAIL_DIMENSIONS.split(',')     
        THUMBAIL_DIMENSIONS = int(lst_dimensions[0]), int(lst_dimensions[1])
    except:
        print(f'Failed to parse THUMBNAIL_DIMENSIONS {THUMBAIL_DIMENSIONS}')
        THUMBAIL_DIMENSIONS = thumbnail_dimensions_defaults

print(f'Thumbnail dimensions {THUMBAIL_DIMENSIONS}')

if IS_OFFLINE:
    s3_client = boto3.client(
        's3',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    s3_client = boto3.client('s3')

def metadataUpdateItem(metadata_url, payload):
    print('Attempting to update metadata. Endpoint: ' + metadata_url + ', Data: ' + str(payload) )
    try:
        #response = requests.put(metadata_url, data = json.dumps(payload))
        requests.put(metadata_url, json = payload)
        response = '{ "response": "metadata successfully updated" }'
    except Error as e:
        print('Failed to update metadata' + e)
        response = "OOOPS! Failed to update metadata"
    return response

def lambda_handler(event, context):
    """
    Description
    ----------
    Download original image from S3 bucket based on event information.
    Create thumbnail of the image and write it into THUMBNAIL_BUCKET

    Based on https://auth0.com/blog/image-processing-in-python-with-pillow/#Installation-and-Project-Setup

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    None


    Scratchpad
    Thumbnail local URL http://localhost:4566/ltd.noooner.dam.core.thumbnails/d7dcd8b8e2b35c19b42b81c6dfdc1280.JPG
    """
    
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print('Received event from bucket ' + bucket + ' for file ' + key)
    except:
        print('OOOPS! Failed to parse event. Here is what was received: ')
        pprint(event)
        return None
    
    try:
        print(f'Attempting to get file {key}')
        original_file = S3Get(s3_client, key, bucket)
        #print('original_file value is ' + str(original_file))
        if original_file is False:
            print(f'OOOPS! File {key} not found in the bucket {bucket}. Exit and return None.')
            return None
    except Exception as e:
        print(e)
        print(f'OOOPS! Failed to get file {key} from the bucket {bucket}')
        return None


    # Image processing commencing
    print('Opening image ' + str(original_file))   
    image = Image.open(original_file)
    image_size = str(image.size)
    format = str(image.format)
    print(f'Image size before thumbnail: {image.size} , image format {format}') 
  
    image.thumbnail(THUMBAIL_DIMENSIONS)
    image_size = str(image.size)
    print(f'Image size after  thumbnail: {image.size}')
    image.save(original_file)
    head, tail = os.path.split(original_file) # read the original filename into tail
    tail = tail.lower() # lower-case the filename for consistency (.JPG -> .jpg)

    # Send thumbnail to S3 bucket, set public-read flag on
    try: 
        print('Sending ' + tail + ' (was ' + key + ') to ' + THUMBNAIL_BUCKET)
        S3Put(s3_client, original_file, THUMBNAIL_BUCKET, tail, True)

    except Error as e:
        print('Failed to send ' + tail + ' to bucket' + THUMBNAIL_BUCKET + ': ' + e)
        return e
        

    # Update metadata
    try:
        tmp_list = tail.split(".")
        ddb_key = tmp_list[0]
        metadata_url = METADATA_ENDPOINT_URL + '?id=' + ddb_key
        print('Sending update request to metadata endpoint ' + metadata_url)
        payload = {
            "thumbnail_url": thumbnail_bucket_url_base + tail,
            "updated_by": "thumbnails function" 
        }
        print('Update payload ' + str(payload))
        response = metadataUpdateItem(metadata_url, payload)
    except Error as e:
        print('Failed to update metadata: ' + e)


    # Tidy up file system
    if os.path.exists(original_file):
        os.remove(original_file)

    return response
