#!/usr/bin/env python3

from app import lambda_handler
from functions import *
import os, boto3, argparse

DOWNLOAD_BUCKET = os.environ.get('DOWNLOAD_BUCKET')
THUMBNAIL_BUCKET = os.environ.get('THUMBNAIL_BUCKET')

parser = argparse.ArgumentParser(description='Create image thumbnail')
parser.add_argument('-f', '--filename', dest='filename', required=True, help="file to process")
args = parser.parse_args()

key = args.filename

event = mockS3Trigger(DOWNLOAD_BUCKET, key)

results = lambda_handler(event, None)

print(f'Received: {results}')
