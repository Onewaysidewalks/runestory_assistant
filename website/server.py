# #Hack logging for debug logs
# from __future__ import print_function
# import sys

from flask import Flask, json
from flask import request

import models
import os
from api import load_data, save_competitive_standings, load_competitive_standings


app = Flask(__name__)
app.json_encoder = models.JsonEncoder

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/api/data.json")
def data():
    return json.jsonify(load_data())

@app.route("/api/competitive_standings.json", methods=["GET", "POST"])
def competitive_standings():
    if request.method == "GET":
        return json.jsonify(load_competitive_standings())
    else:
        save_competitive_standings(request.data)
        return ('', 204)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
