import json, os, time
from pprint import pprint
import urllib.parse
import boto3
from iptcinfo3 import IPTCInfo
from functions import *

#print('Loading function')

IS_OFFLINE = os.environ.get('IS_OFFLINE')
INDEX_TABLE = os.environ.get('INDEX_TABLE')
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET')
DOWNLOAD_BUCKET = os.environ.get('DOWNLOAD_BUCKET')

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

def listSanitiser(list):
    lessThan = 3
    tmp_list = []
    conjunctions = ['and', 'the', 'was']
    
    for each in list:
        if len(each) < lessThan:
            print('Removing item ' + str(each) + ' (less than ' + str(lessThan) + ' chars)')
        elif each in conjunctions:
            print('Removing item ' + str(each) + ' (conjunction)')
        else:
            tmp_list.append(each)
         
    return tmp_list

def addSearchField(info):
    """ Extract fields of interest, lowercase all and add into n_search field """
    str_search = ''
    fields_of_interest = [
            'keywords',
            'caption/abstract',
            'headline',
            'original_filename'
    ]
    for field in fields_of_interest:
        try:
            if info[field]:
                if type(info[field]) is list:
                   mystr = ' '.join(info[field])
                elif type(info[field]) is str:
                   mystr = info[field]
                mystr = mystr.lower()
                str_search = str_search + ' ' + mystr
        except KeyError:
            print('OOOPS! No field ' + field + ' for search')
    
    list_search = str_search.split(' ')
    list_search = list( dict.fromkeys(list_search)) #Remove duplicates from the list_search and place the list in dictionary
    info['n_search'] = listSanitiser(list_search)
    return info

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    
    if variableIsNone(INDEX_TABLE):
        print('Environment variable INDEX_TABLE not set')
        return None
    elif variableIsNone(DOWNLOAD_BUCKET):
        print('Environment variable DOWNLOAD_BUCKET not set')
        return None


    upload_bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print('Bucket is ' + str(upload_bucket) + ', Key is ' + str(key))

    try:
        response = s3_client.get_object(Bucket=upload_bucket, Key=key)
        response_body = response['Body'].read() # StreamingBody to bytes
        tmp_file = '/tmp/' + md5sum(response_body)

        with open(tmp_file, "wb") as binary_file: #Write bytes to file so that IPTCInfo class can access it
            binary_file.write(response_body)

        info = IPTCInfo(tmp_file, force=True, inp_charset='UTF-8') # creates iptcinfo3.IPTCInfo object
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

        upload_time_epoch = int(time.time())

        dict_info = {
            'md5': md5sum(response_body),
            'original_filename': key,
            'upload_time': upload_time_epoch
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
            dict_info = addSearchField(dict_info) # Construct custom search field

            # About DDB schema https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SampleData.html
            #print('Dictionary object dict_info has ' + str(len(dict_info)) + " items")
            writeDictionaryToDDB(dict_info, INDEX_TABLE, ddb_client)
        
        print('Sending ' + key + ' to ' + DOWNLOAD_BUCKET)
        S3Put(s3_client, tmp_file, DOWNLOAD_BUCKET, key)
        print('Deleting ' + key + ' from ' + upload_bucket)
        S3Del(s3_client, key, upload_bucket)

        # Remove tmp_file
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, upload_bucket))
        raise e


