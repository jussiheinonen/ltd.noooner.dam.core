# index.py
'''
Extract metadata from image files

USAGE
python3 index.py -f uploads/2BCBG15.jpg -type iptc

READING
XMP vs RDF: https://stackoverflow.com/questions/4681964/which-to-use-xmp-or-rdf
'''

import os, argparse, sys, boto3
from functions import writeDictionaryToDDB
from exif import Image
import exifread
from iptcinfo3 import IPTCInfo
from pprint import pprint

parser = argparse.ArgumentParser(description='Process image metadata')

parser.add_argument('-f', '--file', dest='filename', required=True)
parser.add_argument('-t', '--type', dest='metadata', default='iptc', help="exif or iptc, Type of metadata to extract", required=True)
args = parser.parse_args()

INDEX_TABLE = os.environ['INDEX_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name = 'localhost',
        endpoint_url = 'http://localhost:4566',
        aws_access_key_id = 'whatever',
        aws_secret_access_key = 'whatever'
    )
else:
    client = boto3.client('dynamodb')

if not os.path.exists(args.filename):
    print("Failed to find image " +  args.filename)
    sys.exit(1)
else:
    print("Processing file " + args.filename)

with open(args.filename, 'rb') as image_file:
    image_bytes = image_file.read()
    print("image_bytes length " + str(len(image_bytes)))
    print('Size fo the object image_bytes: ' + str(sys.getsizeof(image_bytes)) + " bytes")

    if args.metadata == 'exif':
        print('Processing EXIF')
        my_image = Image(image_bytes)

        '''
        if my_image.has_exif:
            print('Image has EXIF metadata')
            print(my_image.list_all())
        '''
        if my_image.has_exif:
            print('Trying exifread') 
            tags = exifread.process_file(image_file, details=True)
            for tag in tags.keys():
                print('Key: ' + str(tag) + 'Value: ' + str(tags[tag]))
        '''   
        else:
            print('No EXIF metadata, running dir against it')
            dir(my_image)
            print('Size fo the object my_image: ' + str(sys.getsizeof(my_image)) + " bytes")
        '''
    if args.metadata == 'iptc':
        info = IPTCInfo(args.filename, force=True, inp_charset='UTF-8') # creates iptcinfo3.IPTCInfo object
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
        dict_info = {}
        for field in fields:
            try:
                if info[field]:
                    dict_info[field] = info[field]
            except KeyError:
                print('Failed to find key ' + field)
        
        if len(dict_info) == 0:
            print('No IPTC data found')
        else:
            #pprint(dict_info)
            #print('==========================')
            # About DDB schema https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SampleData.html
            print('Size fo the object dict_info: ' + str(sys.getsizeof(dict_info)) + " bytes")
            print('Dictionary object dict_info has ' + str(len(dict_info)) + " items")
            writeDictionaryToDDB(dict_info, INDEX_TABLE, client)

