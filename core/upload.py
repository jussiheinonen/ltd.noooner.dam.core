# upload.py

# Receive files from clients and store them in persistent storage
#
# Sending file with curl: curl -i -X POST -F file=@README.md http://localhost:5000/upload
#
# TODO swap local block storage to S3 or similar object storage

import os, sys, boto3, pprint, logging
from botocore.exceptions import ClientError
from pprint import pprint
from flask import Flask,  jsonify, request
from functions import S3BucketExists


BUCKET_NAME = os.environ.get('UPLOAD_BUCKET')
IS_OFFLINE = os.environ.get('IS_OFFLINE')

app = Flask(__name__)
app.config['BUCKET_NAME'] = BUCKET_NAME
app.config['IS_OFFLINE'] = IS_OFFLINE

# boto3.client: https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/s3.html#client
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


BUCKET_EXISTS = S3BucketExists(s3_client, app.config['BUCKET_NAME'] )
if not BUCKET_EXISTS:
    print("WARNING: Bucket " + str(app.config['BUCKET_NAME']) + " does not exist!")
else:
    print("Bucket " + str(app.config['BUCKET_NAME']) + " is accessible")
    
@app.route('/upload', methods=['POST'])
def upload_file():
    #check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 406 # 406 Not Acceptable
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No filename'}), 406 # 406 Not Acceptable        
    if file:
        filename = file.filename
        try:
            response = s3_client.upload_fileobj(file, app.config['BUCKET_NAME'], filename)

            # If running locally send a makeshift S3 trigger to Inded function
            if IS_OFFLINE:
                from index import lambda_handler
                from functions import mockS3Trigger
                event = mockS3Trigger(app.config['BUCKET_NAME'], filename)
                lambda_handler(event, None)

            return jsonify({'OK': 'File ' + filename + ' saved successfully in s3://' + str(app.config['BUCKET_NAME'])}), 200
        except ClientError as e:
            logging.error(e)
            return jsonify(e), 400