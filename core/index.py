# index.py
'''
Extract metadata from image files

USAGE
python3 index.py -f uploads/2BCBG15.jpg -type iptc

'''

import os, argparse, sys
from exif import Image
from iptcinfo3 import IPTCInfo

parser = argparse.ArgumentParser(description='Process image metadata')

parser.add_argument('-f', '--file', dest='filename', required=True)
parser.add_argument('-t', '--type', dest='metadata', help="exif or iptc, Type of metadata to extract", required=True)
args = parser.parse_args()


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

        if my_image.has_exif:
            print('Image has EXIF metadata')
            print(my_image.list_all())
        else:
            print('No EXIF metadata, running dir against it')
            dir(my_image)
            print('Size fo the object my_image: ' + str(sys.getsizeof(my_image)) + " bytes")

    if args.metadata == 'iptc':
        my_image = IPTCInfo(args.filename)
        print(my_image)

