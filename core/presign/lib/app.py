from copy import Error
import json, boto3, logging, os
from pprint import pprint
from botocore.exceptions import ClientError
import mimetypes

default_expiration = 600
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET')
DOWNLOAD_BUCKET = os.environ.get('DOWNLOAD_BUCKET')


'''
PARAMETERS
    method:     get_object or put_object - REQUIRED
    filename:   filename to download or to upload - REQUIRED

TESTING
    Uploading file named 2BCBG15.jpg
        curl -X PUT -T 2BCBG15.jpg \
        $(curl -H "Content-Type: application/json" \
        -X POST https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign \
        -d '{"action": "put_object", "filename": "2BCBG15.jpg"}')

    NOTE:   Uploads and downloads use separate buckets and therefore in order to test download 
            one should move the file from upload bucket to download before attempting to download
            
    Downloading file named 2BCBG15.jpg
        curl --output AFP_8TL7YA.jpg \
        $(curl -H "Content-Type: application/json" \
        -X POST https://tm7do0vu9j.execute-api.eu-west-1.amazonaws.com/presign \
        -d '{"action": "get_object", "filename": "AFP_8TL7YA.jpg"}')  
'''

def getContentTypeFromFileExtension(filename):
    try: 
        extension = '.' + os.path.splitext(filename)[1][1:].lower()
        mimetypes.init()
        return mimetypes.types_map[extension]        
    except Error as e:
        return 'OOOPS! ' + e
    


def lambda_handler(event, context):

    if UPLOAD_BUCKET == None or DOWNLOAD_BUCKET == None:
        print('UPLOAD_BUCKET and DOWNLOAD_BUCKET environment variables unset')
        return None
    
    http_method = event['requestContext']['http']['method']
    print(f"HTTP method is {http_method}")
    if http_method == 'GET':
        #pprint(event)
        try:
            filename =  event['queryStringParameters']['filename']
            action =  event['queryStringParameters']['action']
            try:                
                expiration = event['queryStringParameters']['expiration']
            except:
                expiration = default_expiration
            event['body'] = {"action": action, "filename": filename,  "expiration": expiration }

        except:
            print('Failed to process GET request')

    #pprint(event)

    s3_client = boto3.client('s3')
    
    if type(event['body']) == str:
        # make string type body a dict
        payload = json.loads(event['body'])
    else: 
        payload = event['body']

    print('Contents of the payload is ' + str(payload))    
    try:
        object_name = payload['filename']
    except ClientError as e:
        print('Parameter filename not found')
        logging.error(e)
        return None
    try:
        action = payload['action']
        if action == "get_object":
            bucket_name = DOWNLOAD_BUCKET
            params = {
                'Bucket': bucket_name,
                'Key': object_name
                }
        elif action == "put_object":
            bucket_name = UPLOAD_BUCKET            
            mime_type = getContentTypeFromFileExtension(filename)
            params = {
                'Bucket': bucket_name,
                'Key': object_name,
                'ContentType': mime_type 
                }
        else:
            print('Invalid action ' + str(action) + '. Must be one of the get_object or put_object')
            return None    
    except ClientError as e:
        print('Parameter action not found')
        logging.error(e)
        return None
    try: 
        expiration = payload['expiration']
    except:
        expiration = default_expiration
            
    try:
        response = s3_client.generate_presigned_url(action,
                                                    Params=params,
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    response = {
        'response': response
    }

    # The response contains the presigned URL
    pprint(response)

    return response
