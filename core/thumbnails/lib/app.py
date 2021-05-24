import json, boto3, os
from pprint import pprint
from functions import *
from PIL import Image

IS_OFFLINE = os.environ.get('IS_OFFLINE')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET')
THUMBAIL_DIMENSIONS = os.environ.get('THUMBNAIL_DIMENSIONS') # Environment variable syntax THUMBAIL_DIMENSIONS="480,480"
thumbnail_dimensions_defaults = 360,240

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
    """
    
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key =event['Records'][0]['s3']['object']['key']
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


    # Image processing commence  
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

    print('Sending ' + tail + ' (was ' + key + ') to ' + THUMBNAIL_BUCKET)
    S3Put(s3_client, original_file, THUMBNAIL_BUCKET, tail)

    return None
