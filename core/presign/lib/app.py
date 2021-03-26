import json, boto3, logging, os
from pprint import pprint
from botocore.exceptions import ClientError

'''
PARAMETERS
    method:     get_object or put_object - REQUIRED
    filename:   filename to download or to upload - REQUIRED

TESTING
    Uploading file named 2BCBG15.jpg
        curl -X PUT -T 2BCBG15.jpg \
        $(curl -H "Content-Type: application/json" \
        -X POST https://8ydk0jhm36.execute-api.eu-west-1.amazonaws.com/presign \
        -d '{"method": "put_object", "filename": "2BCBG15.jpg"}')

    NOTE:   Uploads and downloads use separate buckets and therefore in order to test download 
            one should move the file from uploade bucket to download before attempting to download
            
    Downloading file named 2BCBG15.jpg
        curl --output 2BCBG15.jpg \
        $(curl -H "Content-Type: application/json" \
        -X POST https://8ydk0jhm36.execute-api.eu-west-1.amazonaws.com/presign \
        -d '{"method": "get_object", "filename": "2BCBG15.jpg"}')  
'''



def lambda_handler(event, context):
    expiration = 300
    UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET')
    DOWNLOAD_BUCKET = os.environ.get('DOWNLOAD_BUCKET')

    if UPLOAD_BUCKET == None or DOWNLOAD_BUCKET == None:
        print('UPLOAD_BUCKET and DOWNLOAD_BUCKET environment variables unset')
        return None
    

    #pprint(event)

    s3_client = boto3.client('s3')
    
    if type(event['body']) == str:
        # make string type body a dict
        payload = json.loads(event['body'])
    else: 
        payload = event['body']

    print('Contents of the payload is ' + str(payload))
    #print('Payload type is ' + str(type(payload)))
    try:
        object_name = payload['filename']
    except ClientError as e:
        print('Parameter filename not found')
        logging.error(e)
        return None
    try:
        method = payload['method']
        if method == "get_object":
            bucket_name = DOWNLOAD_BUCKET
        elif method == "put_object":
            bucket_name = UPLOAD_BUCKET
        else:
            print('Invalid methode ' + str(method) + '. Must be one of the get_object or put_object')
            return None
    except ClientError as e:
        print('Parameter method not found')
        logging.error(e)
        return None 
    try:
        response = s3_client.generate_presigned_url(method,
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    pprint(response)

    return response
