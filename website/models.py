import flask
from flask.json import JSONEncoder

class JSONSerializable(object):
    def __repr__(self):
        return json.dumps(self.__dict__)

class Character(object):
    def __init__(self):
        pass

class Weapon(object):
    def __init__(self):
        pass

class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Character):
            return obj.__dict__
        elif isinstance(obj, Weapon):
            return obj.__dict__
        else:
            return JSONEncoder.default(self, obj)
