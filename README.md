# Metar Exporter

Not a full exporter, but a node_exporter textfile script.  It's not really the traditional usage of node_exporter, but it's silly to run a daemon process and manage a caching read from NOAA Metar files that are only updated every ~20 minutes.


# Deps:

python-metar - https://github.com/python-metar/python-metar


# Just run it as a cron job... 