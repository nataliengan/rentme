"""
transit.py: Updates csv rental data with distance to the nearest bus 
stop using TransLink Open API.
"""
import glob
import os
import sys
import pandas as pd
import requests
import json

TRANSLINK_STOPS_URL = 'http://api.translink.ca/rttiapi/v1/stops'
TRANSLINK_API_KEY = 'zcXlwHJG2oeZrP574KZK'

def distance_to_nearest_stop(row):
	# TransLink API accepts only latitude/longitude with max of 6 digit after decimal
	lat = '%.6f'%(row['latitude'])
	lon = '%.6f'%(row['longitude'])

	headers = {'accept': 'application/JSON'}
	params = {'apikey': TRANSLINK_API_KEY, 'lat': lat, 'long': lon, 'radius': 2000}
	response = requests.get(TRANSLINK_STOPS_URL, headers=headers, params=params)

	if (response.status_code == 404):
		return None

	stops = response.json()
	distances = [stop['Distance'] for stop in stops]

	print(min(distances))
	return min(distances)

def main():
	# Create export directory if not already created
	EXPORT_DIR='./export_processed/'
	if not os.path.exists(EXPORT_DIR):
	    os.mkdir(EXPORT_DIR)

	# Iterate through each csv file in ./export
	for filepath in glob.glob('./export/*.csv'):
		print(filepath)
		df = pd.read_csv(filepath)

		# Calculate nearest distance to a bus stop for each row
		df['stop_distance'] = df.apply(lambda row: distance_to_nearest_stop(row), axis=1)

		# Get File name
		filename = filepath.rsplit("/", 1)[1]

		# Export processed data (with transit info) to a csv file
		df.to_csv(EXPORT_DIR + filename, index=False)

if __name__ == "__main__":
    main()

