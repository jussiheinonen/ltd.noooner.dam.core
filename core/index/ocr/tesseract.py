#!/usr/bin/env python3

'''
DEPENDENCIES
apk add zlib-dev libjpeg-turbo-dev tesseract-ocr
pip install pytesseract

USAGE
./tesseract.py -f filename

EXAMPLE
$ ./tesseract.py -f ../../uploads/train03.png 
['21:44:59', '', 'Next trains', 'No data available', '', 'At this time, no data is available', '', 'Welcome to Brockley Station', '', ' ', '\x0c']

'''

import argparse
from PIL import Image
import pytesseract

parser = argparse.ArgumentParser(description='Extract text from image')
parser.add_argument('-f', '--filename', dest='filename', required=True, help="file to process")
args = parser.parse_args()
filename = args.filename

'''
with open(tmp_file, "wb") as binary_file: #Write bytes to file so that IPTCInfo class can access it
            binary_file.write(response_body)
'''


image = Image.open(open(filename, 'rb')) # Open the image
config = ('-l eng --oem 1 --psm 3') # Create configuration set as seen in https://www.analyticsvidhya.com/blog/2020/05/build-your-own-ocr-google-tesseract-opencv/
text = pytesseract.image_to_string(image, config=config)
text = text.split('\n') # print text
print(text)


