import urllib.request
from urllib.error import URLError, HTTPError
from datetime import datetime
from datetime import timezone
import argparse
import os
from metar import Metar


URL_PATTERN = "http://tgftp.nws.noaa.gov/data/observations/metar/stations/{}.TXT"
INFLUX_URL = "http://norm:9999/api/v2/write?org=quikstorm.net&bucket=metar&precision=s"
INFLUX_TOKEN = "xBOCW_gH_SpMdHr1op-yQNQBf1B2z_gvfqqnOpEQmWUXW6-l7Yd8x3SlwLSzi2WoCMltmBoeqYo0yYbdMWlndQ=="

## HANDLE ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--station', required=True, action="append", help="Station ID(s)")
args = parser.parse_args()

stations = args.station


def send_to_influx(data):

	try:
		req = urllib.request.Request(INFLUX_URL, data=data.encode('utf-8'), headers={"Content-Type":"text/plain","Authorization":"Token {}".format(INFLUX_TOKEN)})
		resp = urllib.request.urlopen(req)

	except HTTPError as e:
		print("Error code {}".format(e.code))
	except URLError as e:
		print("Unable to connect: {}".format(e.code))


def encode_influx_line(tsp, station, metarTxt):

	obs = Metar.Metar(metarTxt)

	influx_line = "metar,station={} ".format(station)

	influx_line += "temp_f={temp_f},dewpoint_f={dewpoint_f},wind_speed_mph={wind_speed_mph},wind_gust_mph={wind_gust_mph},wind_dir={wind_dir},pressure_in={pressure_in},visibility_miles={visibility_miles}".format(
		temp_f = obs.temp.value(units="F"),
		dewpoint_f = obs.dewpt.value(units="F"),
		wind_speed_mph = obs.wind_speed.value(units="MPH"),
		wind_gust_mph = obs.wind_gust.value(units="MPH"),
		wind_dir = obs.wind_gust.value(),
		pressure_in = obs.press.value("IN"),
		visibility_miles = obs.vis.value("MI")
	)

	if ( obs.precip_1hr != None ):
		influx_line += ",precip_1hr_in={}".format(obs.precip_1hr.value("IN"))
	
	if ( obs.precip_3hr != None ):
		influx_line += ",precip_3hr_in={}".format(obs.precip_3hr.value("IN"))

	if ( obs.precip_6hr != None ):
		influx_line += ",precip_6hr_in={}".format(obs.precip_6hr.value("IN"))

	if ( obs.precip_24hr != None ):
		influx_line += ",precip_24hr_in={}".format(obs.precip_24hr.value("IN"))


	influx_line += " {}".format(int(tsp))

	return influx_line



### Main Script

influx_lines = []

for station in stations:

	try:
		url = URL_PATTERN.format(station)
		with urllib.request.urlopen(url) as f:
			content = f.read().decode('utf-8')

			lines = content.splitlines()
			metar_tsp = datetime.strptime(lines[0].strip(), "%Y/%m/%d %H:%M").replace(tzinfo=timezone.utc).timestamp()
			metar_str = lines[1]

			influx_lines.append(encode_influx_line(metar_tsp, station, metar_str))
			

	except:
		print("Error reading METAR for station {}".format(station))

influx_data = "\n".join(influx_lines)
print(influx_data)

send_to_influx(influx_data)
