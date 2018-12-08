import matplotlib.pyplot as plt
import json
import numpy as np
from collections import defaultdict
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def flatten(L):
	for item in L:
		try:
			yield from flatten(item)
		except TypeError:
			yield item

def mark_boundaries(lng, lat):
	m = defaultdict(list)
	for (a, b) in list(zip(lng, lat)):
		m[a].append(b)
		m[b].append(a)

	for key, value in m.items():
		m[key] = [min(value), max(value)]
	return m
		
def read_json_file(filename):
	json_file = open(filename)
	json_str = json_file.read()
	return json.loads(json_str) 


def get_coords(data):
	states = {}
	for i in range(len(data['features'])):
		us_data = data['features'][i]['geometry']['coordinates']
		meta_data = data['features'][i]['properties']
		array = np.array(us_data).flatten()

		lng = []
		lat = []
		for i, elem in enumerate(flatten(array)):
			if i % 2 == 0:
				lng.append(elem)
			else:
				lat.append(elem)

		states[meta_data['NAME']] = { 'meta_data': meta_data, 'lng': lng, 'lat': lat }
	return states


def between(t, a, b):
	if b < a:
		a, b = b, a

	return a <= t and t <= b

def run_mc(bounds, p, reps=1000):
	lng_min = min(lng) # x axis
	lng_max = max(lng) # x axis
	lat_min = min(lat) # y axis
	lat_max = max(lat) # y axis

	accept_xs = []
	accept_ys = []
	
	reject_xs = []
	reject_ys = []

	for i in range(reps):
		x_rand, y_rand = np.random.uniform(size=2)
		random_x = x_rand * (lng_max - lng_min) + lng_min
		random_y = y_rand * (lat_max - lat_min) + lat_min
		point = Point(random_x, random_y)


#		if between(random_x, bounds[random_x][0], bounds[random_x][1]) and between(random_y, bounds[random_y][0], bounds[random_y][1]): # this one
		if p.contains(point):
			accept_xs.append(random_x)
			accept_ys.append(random_y)
		else:
			reject_xs.append(random_x)
			reject_ys.append(random_y)
		
	return { "accepted": [accept_xs, accept_ys], "rejected": [reject_xs, reject_ys] }
			
	
if __name__ == "__main__":
	data = read_json_file('usa_state_shapes.json')
	states = get_coords(data)
	state_name = 'Texas'
	lng = states[state_name]['lng']
	lat = states[state_name]['lat']
	bounds = mark_boundaries(lng, lat)
	polygon = Polygon(zip(lng, lat))
	v = run_mc(bounds, polygon, 2000)

	plt.figure()
	plt.plot(lng, lat)
	plt.scatter(v['accepted'][0], v['accepted'][1], c='blue', alpha=.3, s=1)
	plt.scatter(v['rejected'][0], v['rejected'][1], c='red', alpha=.3, s=1)
	plt.show()

