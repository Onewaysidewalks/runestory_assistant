from flask import Flask, render_template, json
import models
import os
from api import load_data

app = Flask(__name__)
app.json_encoder = models.CharacterEncoder
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/data.json")
def data():
    return json.jsonify(load_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
