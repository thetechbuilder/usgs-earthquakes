#geoevents/adapters/forms.py

#geoevents:
from geoevents.adapters.usgs.json import EarthquakeAdapter

UPLOAD_ADAPTERS = [None, EarthquakeAdapter()]
