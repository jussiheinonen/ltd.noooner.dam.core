#!/usr/bin/env python3

from pprint import pprint
import time, json, logging
from botocore.exceptions import ClientError


def createDDBObject(dict):
    # construct DynamoDB object from dictionary
    #id = time.time_ns() # Type of int. Poor primary key, replaced by md5 checksum
    id = dict['md5'] # Use md5 checksum as a primary key
    ddb_item = { 'id' : {'S': str(id)} }
    for key, value in dict.items():
        type = isTypeOf(value)
        if type == 'SS': 
            value = list( dict.fromkeys(value)) #remove duplicates on the list / stringset, prevent error "Input collection []  contains duplicates"
        #print("'" + str(key) + "': {" + "'" + type + "':" + "'" + str(value) + "'}")
        type_value = { type : value }
        ddb_item[key] = type_value
    return ddb_item

def isTypeOf(value):
    # data types https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item

    if type(value) is list: # Stringset 
        return 'SS'
    elif type(value) is dict: # Map :
        return 'M'
    else:
        return 'S'

def md5sum(image_bytes):
    import hashlib
    checksum = hashlib.md5(image_bytes).hexdigest()
    return checksum

def mockS3Trigger(bucket, key):
    event = dict(
        {
            "Records": [
            {
                "s3": {
                "bucket": {
                    "name": bucket
                },
                "object": {
                    "key": key
                }
                }
            }
            ]
        }
    )

    return event

def S3BucketExists(s3_client, bucket_name):
    # Boto3 S3 client methods https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    try:
        response = s3_client.head_bucket(Bucket = bucket_name)
        return True
    except:
        return False

def S3Put(s3_client, file_name, bucket_name, object_name=None):
    '''
    :param s3_client: Boto3 client object
    :param file_name: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: target filename in bucket, eg. elisa.jpg
    '''

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True    

def S3ObjectExists(s3_clien, bucket_name, file_name):
    try:
        response = s3_client.head_bucket(
            Bucket = bucket_name,
            Key= file_name
            )
        return True
    except:
        return False

def writeDictionaryToDDB(dict, table_name, client):
    print('writing metadata')
    
    ddb_obj = createDDBObject(dict)
    pprint(ddb_obj)

    resp = client.put_item( 
        TableName=table_name, 
        Item=ddb_obj
        )

    print(str(resp))

