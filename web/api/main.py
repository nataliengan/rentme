from constants import POSTAL_MAP
import flask
import pickle
import requests
import urllib.parse
import os

# Geocode
os.environ["GOOGLE_API_KEY"] = ""
import geocoder

TRANSLINK_STOPS_URL = 'http://api.translink.ca/rttiapi/v1/stops'
TRANSLINK_API_KEY = ''
MODELS_DIR = './models/'

app = flask.Flask(__name__)

@app.route("/predict", methods=['GET'])
def predict():
	sqft = int(flask.request.args.get('sqft'))
	bedrooms = int(flask.request.args.get('bedrooms'))
	bathrooms = int(flask.request.args.get('bathrooms'))
	furnished = int(flask.request.args.get('furnished'))
	laundry = int(flask.request.args.get('laundry'))
	address = flask.request.args.get('address')

	print("sqft", sqft, type(sqft))
	print("bedrooms", bedrooms, type(bedrooms))
	print("bathrooms", bathrooms)
	print("furnished", furnished)
	print("laundry", laundry)
	print("address", address)

	# Get lat lng from address, then get postal code and distance to 
	# nearest bus stop as features
	address = urllib.parse.unquote_plus(address)
	geo_location = geocoder.google(address)
	if geo_location:
		latitude = geo_location.lat
		longitude = geo_location.lng

		print("lat", latitude)
		print("lng", longitude)
		
		# Get distance to nearest bus stop
		postal = geocoder.google([latitude,longitude], method='reverse').postal

		print("postal", postal)
		distance_to_stop = distance_to_nearest_stop(latitude, longitude)
	
	# get prefix of postal code
	postal_prefix = postal.split(' ')[0]

	try: 
		area = POSTAL_MAP[postal_prefix]
	except KeyError:
		# Address is not in target area, return response code error
		return 'Address not in target area'

	# Get model for target area
	model = pickle.load(open(MODELS_DIR + area + ".pkl", "rb"))

	# Consolidate features
	features = [sqft, furnished, laundry, bedrooms, bathrooms, distance_to_stop]

	# Predict rental price
	prediction = model.predict(features).tolist()

	print("Predicted price")

	# Prepare response object with model's predictions
	response = {}
	response['prediction'] = prediction

	return flask.jsonify(response)

def distance_to_nearest_stop(lat, lon):
	# TransLink API accepts only latitude/longitude with max of 6 digit after decimal
	lat = '%.6f'%(lat)
	lon = '%.6f'%(lon)

	headers = {'accept': 'application/JSON'}
	params = {'apikey': TRANSLINK_API_KEY, 'lat': lat, 'long': lon, 'radius': 2000}
	response = requests.get(TRANSLINK_STOPS_URL, headers=headers, params=params)

	# Leave field empty if no response from API
	if (response.status_code == 404):
		return None

	stops = response.json()
	distances = [stop['Distance'] for stop in stops]

	# print(min(distances))
	return min(distances)

if __name__ == "__main__":
	app.run(debug=True)