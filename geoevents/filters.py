#geoevents/filters.py

#django:
from django.utils.translation import gettext_lazy as _

#literati:
from literati.filters_base import (
    Select2MultipleFilterBase, RangeSliderFilterBase,
)

#geoevents:
from geoevents.models_base import GeoeventSource, GeoeventCategory
from geoevents.models import Geoevent

class GeoeventSourceFilter(Select2MultipleFilterBase):
    autocomplete_url = "literati_admin:geoevents:geoeventsource-autocomplete"
    parameter_name = "source__in"
    title = _("source")
    model = GeoeventSource

class GeoeventCategoryFilter(Select2MultipleFilterBase):
    autocomplete_url = "literati_admin:geoevents:geoeventcategory-autocomplete"
    parameter_name = "category__in"
    title = _("category")
    model = GeoeventCategory

class GeoeventFilter(Select2MultipleFilterBase):
    autocomplete_url = "literati_admin:geoevents:geoevent-autocomplete"
    parameter_name = "geoevent__in"
    title = _("geo event")
    model = Geoevent

class ParentGeoeventFilter(GeoeventFilter):
    parameter_name = "parent__in"
    title = _("parent")

class GeoeventMagnitudeFilter(RangeSliderFilterBase):
    parameter_name = "magnitude"
    title = _("magnitude")
    attrs = {
        "step" : 0.1,
        "min" : 0,
        "max" : 10
    }
