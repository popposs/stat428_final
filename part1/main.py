import matplotlib.pyplot as plt
import json, math
import numpy as np
from collections import defaultdict
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# helper function to flatten arrays
def flatten(L):
	for item in L:
		try:
			yield from flatten(item)
		except TypeError:
			yield item

# helper function to create a dictionary of x values to y (to determine whether candidate point is in polygon)
def mark_boundaries(lng, lat):
	m = defaultdict(list)
	for (a, b) in list(zip(lng, lat)):
		m[a].append(b)
		m[b].append(a)

	for key, value in m.items():
		m[key] = [min(value), max(value)]
	return m

# helper function to read in .json format files to objects
def read_json_file(filename):
	json_file = open(filename)
	json_str = json_file.read()
	return json.loads(json_str)

# maps state names to their latitude and longitude points
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

# helper function to check if target t is between a and b
def between(t, a, b):
	if b < a:
		a, b = b, a

	return a <= t and t <= b

# function to run the montecarlo at a default of 1000 repetitions
# returns an object of accepted and rejected coordinates, as well as the acceptance ratios at each iteration
def run_mc(p, lng, lat, reps=1000):
	lng_min = min(lng) # x axis
	lng_max = max(lng) # x axis
	lat_min = min(lat) # y axis
	lat_max = max(lat) # y axis

	accept_xs = []
	accept_ys = []

	reject_xs = []
	reject_ys = []

	acceptance = []
	num_accepted = 0

	for i in range(1, reps):
		x_rand, y_rand = np.random.uniform(size=2)
		random_x = x_rand * (lng_max - lng_min) + lng_min
		random_y = y_rand * (lat_max - lat_min) + lat_min
		point = Point(random_x, random_y)

		if p.contains(point):
			accept_xs.append(random_x)
			accept_ys.append(random_y)
			num_accepted += 1
			acceptance.append(num_accepted / i)
		else:
			reject_xs.append(random_x)
			reject_ys.append(random_y)
			acceptance.append(num_accepted / i)

	return { "accepted": [accept_xs, accept_ys], "rejected": [reject_xs, reject_ys], "acceptance": acceptance }

# Haversine, great circle, from https://gist.github.com/rochacbruno/2883505
# Translates coordinate to km
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

# processes the results and formats / colors the plot
# saves the matplotlib graph
def plot_results(lng, lat, v, state_name, ratio, scaled):
	plt.figure()
	plt.plot(lng, lat)
	plt.scatter(v['accepted'][0], v['accepted'][1], c='blue', alpha=.35, s=3)
	plt.scatter(v['rejected'][0], v['rejected'][1], c='red', alpha=.35, s=3)
	plt.title(state_name + ', Accepted: ' + str(ratio) + '%' + ', Area: %.2f km^2' % scaled , fontsize=10)
	plt.savefig(state_name + '_mc.png')

# entry function that calls all the other ones
# collects all the coordinates by statename and runs the simulations
# returns the estimated area
def entrypoint(state_name, reps, chunks=10):
	lng = states[state_name]['lng']
	lat = states[state_name]['lat']
	polygon = Polygon(zip(lng, lat))
	n = reps
	v = run_mc(polygon, lng, lat, n)
	lng_min = min(lng) # x axis
	lng_max = max(lng) # x axis
	lat_min = min(lat) # y axis
	lat_max = max(lat) # y axis

	accepted = v['acceptance']

	scaled = []
	area = distance([lat_min, lng_min ], [lat_max, lng_min]) * distance([lat_min, lng_min], [lat_min, lng_max])
	for ratio in accepted:
		scaled.append(float(ratio * area))

	return scaled
	# plot_results(lng, lat, v, state_name, ratio, scaled)

# main function that processes importing files and plots errors
if __name__ == "__main__":
	data = read_json_file('usa_states_shapes.json')
	areas = read_json_file('usa_states_areas.json')
	states = get_coords(data)

	for state_name in states.keys():
		print(state_name)
		plt.figure()
		for i in range(5):
			area_points = []
			mc_area = entrypoint('Illinois', 1000)
			for i in mc_area:
				area_points.append(abs(areas['Illinois'] - i) / areas['Illinois'])
			plt.plot(list(range(len(mc_area))), area_points)
		plt.title(state_name, fontsize=10)
		plt.savefig(state_name + '_errorplot.png')

	# for name in states.keys():
	# 	state_name = name
	# 	lng = states[state_name]['lng']
	# 	lat = states[state_name]['lat']
	# 	#bounds = mark_boundaries(lng, lat)
	# 	polygon = Polygon(zip(lng, lat))

	# 	n = 1000
	# 	v = run_mc(polygon, n)
	#	v = run_mc(polygon, lng, lat, n)

	# 	lng_min = min(lng) # x axis
	# 	lng_max = max(lng) # x axis
	# 	lat_min = min(lat) # y axis
	# 	lat_max = max(lat) # y axis

	# 	ratio = 100. * len(v['accepted'][0]) / n
	# 	area = distance([lat_min, lng_min ], [lat_max, lng_min]) * distance([lat_min, lng_min], [lat_min, lng_max])
	# 	scaled = float(ratio * area / 100.)

	# 	print('Accepted: ' + str(ratio) + '%')
	# 	print('Area: %.2f km^2' % scaled)

	#	plot_results(lng, lat, v, state_name, ratio, scaled)
