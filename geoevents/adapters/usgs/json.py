#geoevents/adapters/usgs/json.py

import json
import textwrap
import dateutil.parser
from datetime import timedelta, datetime
from decimal import Decimal

#django:
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.functional import cached_property
from django.utils import timezone

from literati.utils.datetime import Calendar

#geoevents:
from geoevents.adapters.base import UploadAdapterBase
from geoevents.adapters.exceptions import GeoeventException

class EarthquakeAdapter(UploadAdapterBase):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?"
    allowed_lookups = (
        "starttime", "endtime", "updateafter", "minmagnitude"
    )
    timeout = 40

    def format_parameter(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return super().format_parameter(value)

    @cached_property
    def event_category(self):
        return self.get_event_category().objects.get_or_create(
            codename = "earthquake", defaults = { 
                "name" : _("Earthquake")
            })[0]

    @cached_property
    def event_source(self):
        return self.get_event_source().objects.get_or_create(
            codename = "usgs_earthquakes", defaults = {
                "name" : _("USGS Earthquakes")
            })[0]

    def _upload(self, parameters, counter = 10):
        #already atomic transaction
        url = self.get_url(parameters)

        response = self.get(url)

        if response.status_code == 400:
            if "starttime" in parameters and counter:
                start_time = parameters["starttime"]
                end_time = parameters.get("endtime", Calendar.get_now().date())

                diff = (end_time - start_time) / 2
                if diff >= timedelta(days = 1):
                    p1 = parameters
                    p2 = parameters.copy()
                    p2["starttime"] = p1["endtime"] = start_time + diff

                    result_left = self._upload(p1, counter - 1)
                    result_right = self._upload(p2, counter - 1)
                    return { 
                        k: result_left.get(k, 0) + result_right.get(k, 0) 
                        for k in set(result_left) | set(result_right) 
                    }
            raise GeoeventException(
                message = textwrap.shorten(response.text, width = 250))
        #process data:
        data = json.loads(response.text)

        created = 0
        updated = 0
        errors = 0
        if "features" in data:
            for feature in data["features"]:
                try:
                    feature_data = self.clean_feature(feature)
                except (ValueError, KeyError):
                    errors += 1
                #except TypeError:
                #    raise Exception(feature)
                else:
                    obj, is_created = self.model.objects.update_or_create(
                        uid = feature_data["uid"],
                        source = self.event_source,
                        defaults = feature_data
                    )
                    created += is_created

            updated = len(data["features"]) - errors - created

        return { 
            "created" : created, 
            "updated" : updated,
            "errors" : errors,
        }

    def clean_feature(self, feature):
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]

        data = {
            "uid" : feature["id"],
            "name" : properties["title"],
            "magnitude" : properties["mag"],
            "category" : self.event_category,
            "source" : self.event_source,
            "date_recorded" : datetime.fromtimestamp(properties["time"]/1000),
            #longitude:
            "lon" :  Decimal(coordinates[0]),
            #latitude:
            "lat" : Decimal(coordinates[1]),
        }
        return data


    def clean_parameters(self, query_string):
        parameters = super().clean_parameters(query_string)
        parameters["format"] = "geojson"

        if "starttime" in parameters and "end_time" in parameters:
            if parameters["starttime"] > parameters["endtime"]:
                raise ValidationError(_(
                    "Start time cannot be more than the end time"))

        return parameters

    def clean_starttime(self, parameters):
        try:
            start_time = dateutil.parser.parse(parameters["starttime"]).date()
        except ValueError:
            raise ValidationError(_(
                "Invalid start time given"))

        if start_time > Calendar.get_now().date():
            raise ValidationError(_(
                "Start time cannot be more than current date"))
        return start_time

    def clean_endtime(self, parameters):
        try:
            end_time = dateutil.parser.parse(parameters["endtime"]).date()
        except ValueError:
            raise ValidationError(_(
                "Invalid end time given"))

        if end_time > Calendar.get_now().date():
            raise ValidationError("End time cannot be more than current date")
        return end_time
