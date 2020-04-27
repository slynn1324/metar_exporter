# Metar Exporter

Not a full exporter, but a node_exporter textfile script.  It's not really the traditional usage of node_exporter, but it's silly to run a daemon process and manage a caching read from NOAA Metar files that are only updated every ~20 minutes.

# Dependencies:

- Python 3
- python-metar - https://github.com/python-metar/python-metar

```
pip3 install metar
```

# Running

```
python3 metar_exporter.py -s {stationId}
```


```
usage: metar_exporter.py [-h] -s STATION [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -s STATION, --station STATION
                        Station ID(s)
  -o OUTPUT, --output OUTPUT
                        Output File
```

Install it as a cronjob and set the output file into your node_exporter textfiles directory.

