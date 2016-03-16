import yaml
import models

import os
from os import listdir
from os.path import isfile, join

import urllib
from PIL import Image
from resizeimage import resizeimage

#Poor mans configuration!
IMAGE_OUTPUT_LOCATION = 'build/images/'
RAW_IMAGE_OUTPUT_LOCATION = 'build/raw_images/'
INGESTION_DATA_LOCATION = 'build/data.yaml'

#Method that loads and saves all character/weapon images found in the data model in an images/ folder
def pullImages(data):
    fileNames = []
    for charClass in data['Characters']:
        for character in data['Characters'][charClass]:

            if isinstance(data['Characters'][charClass][character], dict):
                fileName = '%s.png' % (data['Characters'][charClass][character]['Id']);
                iconUrl = data['Characters'][charClass][character]['IconUrl']
            else:
                fileName = '%s.png' % (data['Characters'][charClass][character].__dict__['Id']);
                iconUrl = data['Characters'][charClass][character].__dict__['IconUrl']

            if fileName and iconUrl:
                fileNames.append(fileName)
                print 'processing %s' % fileName
                urllib.urlretrieve(iconUrl, '%s%s' % (RAW_IMAGE_OUTPUT_LOCATION, fileName))
                
    return fileNames

def resizeImages(fileNames):
    for fileName in fileNames:
        with open('%s%s' % (RAW_IMAGE_OUTPUT_LOCATION, fileName), 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_contain(image, [100, 100])
                cover.save('%s%s' % (IMAGE_OUTPUT_LOCATION, fileName), image.format)

def main():
    print 'performing imaging creation...'
    dataYaml = yaml.load(stream=file(INGESTION_DATA_LOCATION))

    resizeImages(pullImages(dataYaml))

if __name__ == '__main__':
    main()
