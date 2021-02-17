# upload.py

# Receive files from clients and store them in persistent storage
#
# Sending file with curl: curl -i -X POST -F file=@README.md http://localhost:5000/upload
#
# TODO swap local block storage to S3 or similar object storage

import os
from flask import Flask,  jsonify, request

UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    print("Upload directory " + UPLOAD_FOLDER + " does not exist")
    try:
        os.mkdir(UPLOAD_FOLDER)
        print("Upload directory " + UPLOAD_FOLDER + " created")
    except TypeError as e:
        print("Failed to create upload directory " + UPLOAD_FOLDER + ". Error " + e)

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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'ok': 'File ' + filename + ' saved successfully'}), 200
       