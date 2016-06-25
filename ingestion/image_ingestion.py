##This file should be ran AFTER overrides have been ran, to pick up global character information, OR, manually add the png files for global characters, and change the source data location
##After running this, one will need to run a "GLUE" command to actually generate a sprite sheet, as well as the css file for it: glue build/images/ build/final_css --png8

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
INGESTION_DATA_LOCATION = 'build/basedata.yaml'

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

    fileNames.append('10000.png') #mage leah

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
