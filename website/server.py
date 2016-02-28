from flask import Flask, json
import models
import os
from api import load_data

app = Flask(__name__)
app.json_encoder = models.JsonEncoder
@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/api/data.json")
def data():
    return json.jsonify(load_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
