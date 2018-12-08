import matplotlib.pyplot as plt
import json, math
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

		if p.contains(point):
			accept_xs.append(random_x)
			accept_ys.append(random_y)
		else:
			reject_xs.append(random_x)
			reject_ys.append(random_y)
		
	return { "accepted": [accept_xs, accept_ys], "rejected": [reject_xs, reject_ys] }
			
# Haversine, great circle, from https://gist.github.com/rochacbruno/2883505
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d
	
if __name__ == "__main__":
	data = read_json_file('usa_state_shapes.json')
	states = get_coords(data)
	state_name = 'Illinois'
	lng = states[state_name]['lng']
	lat = states[state_name]['lat']
	bounds = mark_boundaries(lng, lat)
	polygon = Polygon(zip(lng, lat))

	n = 1000
	v = run_mc(bounds, polygon, n)

	lng_min = min(lng) # x axis
	lng_max = max(lng) # x axis
	lat_min = min(lat) # y axis
	lat_max = max(lat) # y axis

	ratio = 100. * len(v['accepted'][0]) / n
	area = distance([lat_min, lng_min ], [lat_max, lng_min]) * distance([lat_min, lng_min], [lat_min, lng_max])

	print('Accepted: ' + str(ratio) + '%')
	print('Area: ' + str(ratio * area / 100.) + ' km 2')

	plt.figure()
	plt.plot(lng, lat)
	plt.scatter(v['accepted'][0], v['accepted'][1], c='blue', alpha=.3, s=1)
	plt.scatter(v['rejected'][0], v['rejected'][1], c='red', alpha=.3, s=1)
	plt.show()

