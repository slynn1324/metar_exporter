import urllib.request
from datetime import datetime
from datetime import timezone
import argparse
import os
from metar import Metar


URL_PATTERN = "http://tgftp.nws.noaa.gov/data/observations/metar/stations/{}.TXT"


## HANDLE ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--station', required=True, action="append", help="Station ID(s)")
parser.add_argument('-o', '--output', required=False, help="Output File")
args = parser.parse_args()

stations = args.station
output_file = args.output

def add_metric_value(metricName, station, val):
	metrics.append('metar_{}{{station="{}"}} {}'.format(metricName, station, val))


def add_metric(obs, fieldName, metricName, units, station):

	obs_val = getattr(obs, fieldName)
	
	val = 0.0
	if ( obs_val != None ):
		if units != None:
			val = obs_val.value(units=units)
		else:
			val = obs_val.value()

	add_metric_value(metricName, station, val)


def add_metar_metrics(station, metarTxt):

	obs = Metar.Metar(metarTxt)

	add_metric(obs, "temp", "temperature_f", "F", station)
	add_metric(obs, "dewpt", "dewpoint_f", "F", station)
	add_metric(obs, "wind_speed", "wind_speed_mph", "MPH", station)
	add_metric(obs, "wind_gust", "wind_gust_mph", "MPH", station)
	add_metric(obs, "wind_dir", "wind_direction_deg", None, station)
	add_metric(obs, "press", "pressure_in", "IN", station)
	add_metric(obs, "vis", "visibility_miles", "MI", station)
	add_metric(obs, "precip_1hr", "precip_1hr", "IN", station)

	# we skip these metrics if missing, as they only publish on the 3 and 6 hour marks, and otherwise would overwrite 
	# previous stats
	if ( obs.precip_3hr != None ):
		add_metric(obs, "precip_3hr", "precip_3hr", "IN", station)

	if ( obs.precip_6hr != None ):
		add_metric(obs, "precip_6hr", "precip_6hr", "IN", station)

	if ( obs.precip_24hr != None ):
		add_metric(obs, "precip_24hr", "precip_24hr", "IN", station)
	# adD_metric(obs, "sky", )
	

### Main Script

metrics = []

for station in stations:

	try:
		url = URL_PATTERN.format(station)
		with urllib.request.urlopen(url) as f:
			content = f.read().decode('utf-8')

			for line in content.splitlines():
				if line.startswith(station):
					add_metar_metrics(station, line)
				else:
					# the other line should be the observation timestamp
					try:
						metar_tsp = datetime.strptime(line.strip(), "%Y/%m/%d %H:%M").replace(tzinfo=timezone.utc).timestamp()
						add_metric_value("observation_time", station, int(metar_tsp))

					except:
						pass

		# it worked
		add_metric_value("up", station, 1)
	except:
		add_metric_value("up", station, 0)


if ( output_file != None ):

	# use a temprary file to get an atomic write of the target file
	tmp_file = output_file + ".tmp"

	with open(tmp_file, 'w') as f:
		for m in metrics:
			f.write(m)
			f.write("\n")

	os.rename(tmp_file, output_file)
else:
	for m in metrics:
		print(m)
