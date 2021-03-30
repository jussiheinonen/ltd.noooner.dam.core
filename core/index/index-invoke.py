#!/usr/bin/env python3

from index import lambda_handler
import json, os, sys, argparse, boto3
from functions import *

'''
CLI tool for...
    1. Uploading a file to upload bucket
    2. Sending mock S3 trigger to index.lambda_handler()

To bulk feed images...
    for file in $(ls ../uploads/); do
        ./index-invoke.py --filename ../uploads/${file} --bucketname ltd.noooner.dam.core.upload
    done
'''
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET')
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if UPLOAD_BUCKET == None:
    print('Environment variable UPLOAD_BUCKET undefined')
    sys.exit(0)

parser = argparse.ArgumentParser(description='Process image metadata')

parser.add_argument('-f', '--filename', dest='filename', required=True, help="file to upload into S3 bucket")
parser.add_argument('-b', '--bucketname', dest='bucket', required=True, help="name of the S3 bucket")
args = parser.parse_args()

bucket = args.bucket
filename = args.filename

if IS_OFFLINE:
    s3_client = boto3.client(
        's3',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'test',
        aws_secret_access_key = 'test'
    )

if not S3BucketExists(s3_client, bucket):
    print("Bucket " + bucket + " does not exist")
    sys.exit(0)

if not os.path.isfile(filename):
    print("File " + filename + " does not exist")
    sys.exit(0)

head, tail = os.path.split(filename)

S3Put(s3_client, filename, bucket, tail)
#sys.exit(0)

event = mockS3Trigger(bucket, tail)
lambda_handler(event, None)

'''
with open('s3invoke.json', 'rb') as json_data:
    event = json.load(json_data)
    lambda_handler(event, None)
'''
    