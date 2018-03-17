#geoevents/urls/admin.py

#django:
from django.conf.urls import include, url

urlpatterns = [
    url(r'^autocomplete/', include('geoevents.urls.dal')),
]
