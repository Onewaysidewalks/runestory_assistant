# #Hack logging for debug logs
#from __future__ import print_function
#import sys

import yaml
import os
from settings import APP_STATIC
import json
import sys

STATIC_DATA = dict()
COMPETITIVE_STANDINGS = dict()

DATA_FILE_LOCATION = 'data.yaml'

def load_data():
    global STATIC_DATA #TODO: use a real caching system...
    if len(STATIC_DATA) is 0:
        print('Stale cache, loading file')
        STATIC_DATA = yaml.load(stream=file(os.path.join(APP_STATIC, DATA_FILE_LOCATION)))
    return STATIC_DATA

def load_competitive_standings():
    return COMPETITIVE_STANDINGS

def save_competitive_standings(jsonData):
    global COMPETITIVE_STANDINGS #TODO: use a real caching system...
    serverResult = json.loads(jsonData)
    COMPETITIVE_STANDINGS[serverResult['server']] = serverResult
