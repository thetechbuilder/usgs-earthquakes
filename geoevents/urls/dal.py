#geoevents/urls/dal.py

#django:
from django.conf.urls import url

#geoevents:
from geoevents.views.dal import (
    GeoeventAutocomplete,
    GeoeventCategoryAutocomplete,
    GeoeventSourceAutocomplete,
)

urlpatterns = [
    #GeoeventAutocomplete:
    url(r"^geoevent-autocomplete/$", GeoeventAutocomplete.as_view(),
        name="geoevent-autocomplete"),

    #GeoeventCategory:
    url(r"^geoeventcategory-autocomplete/$", GeoeventCategoryAutocomplete.as_view(),
        name="geoeventcategory-autocomplete"),
    url(r"^activegeoeventcategory-autocomplete/$", 
        GeoeventCategoryAutocomplete.as_view(limit_choices_to = { "is_active" : True }),
        name="activegeoeventcategory-autocomplete"),

    #GeoeventCategoryAutocomplete:
    url(r"^geoeventsource-autocomplete/$", GeoeventSourceAutocomplete.as_view(),
        name="geoeventsource-autocomplete"),
    url(r"^activegeoeventsource-autocomplete/$", 
        GeoeventSourceAutocomplete.as_view(limit_choices_to = { "is_active" : True }),
        name="activegeoeventsource-autocomplete"),
]
