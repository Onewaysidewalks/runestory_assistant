import yaml
import models

import os
from os import listdir
from os.path import isfile, join

import urllib
from PIL import Image
from resizeimage import resizeimage

#Poor mans configuration!
INGESTION_DATA_LOCATION = 'build/basedata.yaml'
OVERRIDE_DATA_LOCATION = 'overrides/overrides.yaml'
OUTPUT_LOCATION = 'build/data.yaml'
IMAGE_OUTPUT_LOCATION = 'build/images/'
RAW_IMAGE_OUTPUT_LOCATION = 'build/raw_images/'

#Method that loads and saves all character/weapon images found in the data model in an images/ folder
#TODO move to ingestion piece, because thats what it really is
def pullImages(data):
    fileNames = []
    for charClass in data['Characters']:
        for character in data['Characters'][charClass]:
            print data['Characters'][charClass][character]
            if data['Characters'][charClass][character].__dict__['IconUrl']:
                fileName = '%s.png' % (data['Characters'][charClass][character].__dict__['Id']);
                fileNames.append(fileName)
                urllib.urlretrieve(data['Characters'][charClass][character].__dict__['IconUrl'], '%s%s' % (RAW_IMAGE_OUTPUT_LOCATION, fileName))
    return fileNames

def resizeImages(fileNames):
    for fileName in fileNames:
        with open('%s%s' % (RAW_IMAGE_OUTPUT_LOCATION, fileName), 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_contain(image, [100, 100])
                cover.save('%s%s' % (IMAGE_OUTPUT_LOCATION, fileName), image.format)

#NTOE: This method will replace lists of items ENTIRELY, not merge
#them together. As such, lists will need to be replaced as a WHOLE
def mergeYaml(baseLine, overrides):
    for k,v in overrides.iteritems():
        if isIterable(baseLine):
            if k not in baseLine:
                baseLine[k] = v
            else:
                baseLine[k] = mergeYaml(baseLine[k], v) #Recursively call for sub objects
        else:
            setattr(baseLine, k, v)

    return baseLine

def isIterable(someObj):
    try:
        iterator = iter(someObj)
    except TypeError:
        return False
    else:
        return True


def main():
    print 'performing merge...'

    ingestionYaml = yaml.load(stream=file(INGESTION_DATA_LOCATION))

    overridesYaml = yaml.safe_load(stream=file(OVERRIDE_DATA_LOCATION))

    finalYaml = mergeYaml(ingestionYaml, overridesYaml)

    # resizeImages(pullImages(finalYaml))



    #Now write the file in all its yamlly glory (first creating the directory if necessary)
    if not os.path.exists(os.path.dirname(OUTPUT_LOCATION)):
        try:
            os.makedirs(os.path.dirname(OUTPUT_LOCATION))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(OUTPUT_LOCATION, 'w') as yaml_file: #We use safe_dump, to remove the !!python declarations from the file
        yaml_file.write(yaml.dump(finalYaml, default_flow_style=False, encoding=('utf-8'), allow_unicode=True))

if __name__ == '__main__':
    main()
