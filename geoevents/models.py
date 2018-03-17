#geoevents/models.py

#django:
from django.db import models
from django.utils.translation import gettext_lazy as _

#literati_geonames
from literati_geonames.models_base import AdminDivision

#geoevents:
from geoevents.models_base import GeoeventBase

class Geoevent(GeoeventBase):
    admin = models.ForeignKey(AdminDivision, null = True, blank = False,
        verbose_name = _("administrative division"))

    class Meta:
        verbose_name = _("geo event")
        verbose_name_plural = _("geo events")
        permissions = (
            ("autocomplete_geoevent", "Can autocomplete geoevent"),
            ("access_magnitudestats_geoevent", "Can access magnitude geoevent stats"),
            ("access_activity_geoevent", "Can access geoevent activity"),
        )
