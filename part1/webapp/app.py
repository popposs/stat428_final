from flask import Flask, request, make_response, Response, jsonify, render_template, url_for, send_file
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import time, os, json, io, random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/send')
def send():
	with open('usa_state_shapes.json') as f:
		data = json.load(f)
		return json.dumps(data, indent=4)

@app.route('/plot/<state_name>')
def plot_png(state_name):
	name = state_name.lower().capitalize()
	return send_file('mc_states/' + state_name + '_mc.png', mimetype='image/png')

@app.route('/states')
def get_states():
	with open('state_names.json') as f:
		data = json.load(f)
		return json.dumps(data, indent=4)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True, host='0.0.0.0')

