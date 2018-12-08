from flask import Flask, request, make_response, Response, jsonify, render_template, url_for
from flask_cors import CORS
from multiprocessing import Process, Value
import time
import os
import json
from pprint import pprint

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('new_index.html')

@app.route('/send')
def send():
    with open('usa_state_shapes.json') as f:
        data = json.load(f)
        return json.dumps(data, indent=4)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host='0.0.0.0')
