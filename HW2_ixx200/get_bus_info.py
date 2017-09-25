# PULL BUS DATA FROM METRO API
# Return a list of bus information

import sys
import pandas as pd
import sys
import json
import urllib3
import pprint
import csv

def setup(api_key, bus_line):

	'''
	This function creates a API URL based on user inputs

	Args:
		api_key (str): private API key the use received from MTA API service
		bus_line (str): a bus line of interest (i.e. b27)

	Return: a full url including API request details, API Key, and Buse Line of Interest

	'''

	return "http://bustime.mta.info/api/siri/vehicle-monitoring.json?key=" + api_key + "&VehicleMonitoringDetailLevel=calls&LineRef=" + bus_line



def callAPI(url):

	'''
	This function triggers a url link for RESTful API Call

	Args:
		ulr (str): a full url link including API address, API Key, and Bus Line of interest

	Return: 
		r.data: raw json data receive from the API call

	'''

	http = urllib3.PoolManager()
	r = http.request('GET', url)
	
	if r.status == 200:
		print ('API Request Succeeded with Request Code: ' + str(r.status))
		print ('==================================================')
	else:
		print ('Check Again. Request Code: ' + str(r.status))
		print ('==================================================')

	return r.data



def parseData(bus_line, raw_data):

	'''
	This function prints out key location information regarding a bus line at the request time; it also returns the data in a json format

	Args:
		bus_line (str): bus line of interest provided by the user 
		raw_data (str): bus location data in plain text format received from API request

	Return: bus location data in json format

	'''

	json_data = json.loads(raw_data)

	numBus = len(json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'])

	print("Bus Line : " + bus_line)
	print("Number of Active Buses : " + str(numBus))

	print ('==================================================')

	return json_data



def extractStopData(json_data):
	
	'''
	This function exports next stop info of each bus in the line of interest

	Args:
		json_data (json object): bus locaiton data in json format

	Return: a array of dictionary including Bus ID, Latitude,Longitude,Stop Name,Stop Status

	'''

	stopData = []

	numBus = len(json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'])

	for i in range(numBus):

		latitude = json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'][i]['MonitoredVehicleJourney']\
							['VehicleLocation']['Latitude']

		longitude = json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'][i]['MonitoredVehicleJourney']\
							['VehicleLocation']['Longitude']

		try:

			StopName = json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'][i]['MonitoredVehicleJourney']\
								['OnwardCalls']['OnwardCall'][0]['StopPointName']

			StopStatus = json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity'][i]['MonitoredVehicleJourney']\
								['OnwardCalls']['OnwardCall'][0]['Extensions']['Distances']['PresentableDistance']
		
		except: 
			StopName = 'N/A'

			StopStatus = 'N/A'	

		print("Bus " + str(i+1) + " is at latitude " + str(latitude) + " and longitude " + str(longitude) + " at Stop : " + StopName + " (" + StopStatus + ")")

		try: 

			stopData.append({'Bus ID': i+1, 'Latitude': latitude, 'Longitude': longitude, 'Stop Name': StopName, 'Stop Status': StopStatus})

		except:

			stopData[0] = {'Bus ID': i+1, 'Latitude': latitude, 'Longitude': longitude, 'Stop Name': StopName, 'Stop Status': StopStatus}

	print ('==================================================')

	return stopData



def export2CSV(stopData, file_name):

	'''
	This function exports the list of Stop Data of a bus line into CSV

	Args:
		stopData (array): a list of dictionary including Bus ID, Latitude, Longitude, Stop Name, Stop Status
		file_name (str): user input file name

	Return: None

	'''
	try:
		keys = stopData[0].keys()

		with open(file_name, 'w') as output_file:
			dict_writer = csv.DictWriter(output_file, keys)
			dict_writer.writeheader()
			dict_writer.writerows(stopData)

		print('Exported Stop Data to CSV Successful. Check the File at: ' + "./data/" + file_name)

	except:
		e = sys.exc_info()
		print('Export Stop Data to CSV Failed: ' + str(e))


def exportRawData(json_data):

	'''
	This function exports bus location data to a file with the request timestamp

	Args:
		json_data (json object): bus locaiton data in json format

	Return: None

	'''
	
	fileName = './data/bus_location_' + str(json_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['ValidUntil'].split('.')[0]) + '.txt'
	with open(fileName, 'w') as outfile:
		json.dump(json_data, outfile)



def main():

	'''
	This is the main execution workflow of this script; it standardize user input and calls all sub-functions

	It takes in 2 parameters passed in by an user and stores in api_key and bus_line respectively. 

	Expected user call: python show_bus_locations.py xxxxx-xxxxx-xxxxx-xxxxx-xxxxx B52 B52.csv

	'''
	try:
		api_key = sys.argv[1]
		bus_line = str(sys.argv[2]).upper()
		file_name = sys.argv[3]

		url = setup(api_key, bus_line)
		raw_data = callAPI(url)
		json_data = parseData(bus_line, raw_data)
		stopData = extractStopData(json_data)
		export2CSV(stopData, file_name)
		exportRawData(json_data)

	except:
		e = sys.exc_info()
		print("Something went wrong: " + str(e))
		print("Please confirm if you enter the correct bus line number.")
		sys.exit(1)


if __name__ == "__main__":
	main()