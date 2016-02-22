import yaml
import os
from settings import APP_STATIC

STATIC_DATA = dict()
DATA_FILE_LOCATION = 'data.yaml'

def load_data():
    global STATIC_DATA #THIS IS BAD AND I AM SO SORRY
    if len(STATIC_DATA) is 0:
        print 'Stale cache, loading file'
        STATIC_DATA = yaml.load(stream=file(os.path.join(APP_STATIC, DATA_FILE_LOCATION)))
    return STATIC_DATA
