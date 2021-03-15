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


UPLOAD_FOLDER = './uploads'
BUCKET_NAME = os.environ.get('BUCKET_NAME')
BUCKET_EXISTS = False
ENDPOINT_URL = 'http://localhost:4566'
STORAGE_TYPE = 'S3' # S3 or FS (local file system)
IS_OFFLINE = os.environ.get('IS_OFFLINE')



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BUCKET_NAME'] = BUCKET_NAME
app.config['ENDPOINT_URL'] = ENDPOINT_URL
app.config['STORAGE_TYPE'] = STORAGE_TYPE
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

if app.config['STORAGE_TYPE'] == 'FS':
    if not os.path.exists(UPLOAD_FOLDER):
        print("Upload directory " + UPLOAD_FOLDER + " does not exist")
        try:
            os.mkdir(UPLOAD_FOLDER)
            print("Upload directory " + UPLOAD_FOLDER + " created")
        except TypeError as e:
            print("Failed to create upload directory " + UPLOAD_FOLDER + ". Error " + e)
elif app.config['STORAGE_TYPE'] == 'S3':
    BUCKET_EXISTS = S3BucketExists(s3_client, app.config['BUCKET_NAME'] )
    if not BUCKET_EXISTS:
        print("WARNING: Bucket " + str(app.config['BUCKET_NAME']) + " does not exist!")
    
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
        if app.config['STORAGE_TYPE'] == 'FS':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'ok': 'File ' + filename + ' saved successfully'}), 200
        elif app.config['STORAGE_TYPE'] == 'S3':
            try:
                response = s3_client.upload_fileobj(file, app.config['BUCKET_NAME'], filename)
            except ClientError as e:
                logging.error(e)
                return jsonify(e), 400
            return jsonify({'ok': 'File ' + filename + ' saved successfully in S3'}), 200
       