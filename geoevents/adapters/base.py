#geoevents/adapters/base.py
import requests

#django:
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _, gettext_lazy

#literati:
from literati.uploads.base import UploadAdapterBase as _UploadAdapterBase

#geoevents:
from geoevents.models_base import GeoeventCategory
from geoevents.models import Geoevent

class UploadAdapterBase(_UploadAdapterBase):
    model = Geoevent

    def get_event_category(self):
        return self.model._meta.get_field("category").rel.to

    def get_event_source(self):
        return self.model._meta.get_field("source").rel.to
