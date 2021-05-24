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
        ddb_type = isTypeOf(value)
        if ddb_type == 'SS':
            value = list( dict.fromkeys(value)) #remove duplicates on the list / stringset, prevent error "Input collection []  contains duplicates"
        if ddb_type == 'N':
            value = str(value)
        type_value = { ddb_type : value }
        ddb_item[key] = type_value
    return ddb_item

def isTypeOf(value):
    # data types https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item

    if type(value) is list: # Stringset 
        return 'SS'
    elif type(value) is dict: # Map
        return 'M'
    elif type(value) is int:
        '''
        Integers stored as a type Number
        Int must be converted to String before inserting into DynamoDB
        More info https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/dynamodb/types.html
        '''
        return 'N'
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

def mockQueryResponse():
    response = dict(
            {
                "Items": [
                {
                    "description": "image A description",
                    "download_url": "https://s3.com/A",
                    "thumbnail_url": "https://thumb.com/A",
                    "created": "20210413",
                    "keywords_match": ['word1','word2'],
                    "keywords_nomatch": ['word10', 'word11']

                },
                {
                    "description": "image B description",
                    "download_url": "https://s3.com/B",
                    "thumbnail_url": "https://thumb.com/B",
                    "created": "20210412",
                    "keywords_match": ['word1','word2', 'word10'],
                    "keywords_nomatch": ['word11']                    
                }
                ]
            }
    )
    return response

def S3BucketExists(s3_client, bucket_name):
    # Boto3 S3 client methods https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    try:
        response = s3_client.head_bucket(Bucket = bucket_name)
        return True
    except:
        return False

def S3Del(s3_client, file_name, bucket_name):
    '''
    :param s3_client: Boto3 client object
    :param file_name: File to delete
    :param bucket_name: Bucket to delete from
    '''

    try:
        response = s3_client.delete_object(
            Key=file_name, 
            Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True    

def S3Get(s3_client, file_name, bucket_name):
    '''
    :param s3_client: Boto3 client object
    :param file_name: File to get
    :param bucket_name: Bucket to get from

    Returns
    ------
    File object

    '''

    try:
        response = s3_client.get_object(
            Key=file_name,
            Bucket=bucket_name)

    except ClientError as e:
        logging.error(e)
        return False

    lst_file_ext = file_name.split('.')
    file_ext = lst_file_ext[-1]
    response_body = response['Body'].read() # StreamingBody to bytes
    tmp_file = '/tmp/' + md5sum(response_body) + '.' + file_ext
    with open(tmp_file, "wb") as binary_file: #Write bytes to a file
        binary_file.write(response_body)

    return tmp_file

def S3Put(s3_client, file_name, bucket_name, object_name=None, public_read=None):
    '''
    :param s3_client: Boto3 client object
    :param file_name: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: target filename in bucket, eg. elisa.jpg
    :param public_read: If True switch public-read flag on for the object
    '''

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    try:
        if public_read:
            response = s3_client.upload_file(
                file_name, 
                bucket_name, 
                object_name,
                ExtraArgs={'ACL': 'public-read'}
                )    
        else:
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

def variableIsNone(var_name):
    if var_name == None:
        return True
    else:
        return False
    

def writeDictionaryToDDB(dict, table_name, client):
    print('writing metadata')
    
    ddb_obj = createDDBObject(dict)
    pprint(ddb_obj)

    try:
        resp = client.put_item( 
            TableName=table_name, 
            Item=ddb_obj)
        
    except ClientError as e:
        logging.error(e)
        return False
    return True

    

