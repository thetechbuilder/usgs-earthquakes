#geoevents/models.py

#django:
from django.db import models
from django.utils.translation import gettext_lazy as _

#literati:
from literati.models_base import CategoryBase, Notable

class GeoeventCategory(CategoryBase):
    codename = models.CharField(max_length = 20, null = True,
        help_text = _("Classification codename of geo event category. ")
    )
    last_modified = models.DateField(auto_now = True)

    def __str__(self):
        return "{} | {} | {}".format(self.id, self.codename, self.name) 

    class Meta:
        verbose_name = _("event category")
        verbose_name_plural = _("event categories")
        permissions = (
            ("autocomplete_geoeventcategory", "Can autocomplete geoevent category"),
        )

class GeoeventSource(CategoryBase):
    details_url = models.URLField(
        verbose_name = _("details url"), 
        blank = True, null = True)
    codename = models.CharField(max_length = 20, null = True,
        help_text = _("Classification codename of geo event source. ")
    )
    
    class Meta:
        verbose_name = _("event source")
        verbose_name_plural = _("event sources")
        permissions = (
            ("autocomplete_geoeventsource", "Can autocomplete geoevent source"),
        )

class GeoeventBase(Notable):
    parent = models.ForeignKey("self", null = True, blank = True)

    #generic properties:
    name = models.CharField(max_length = 200, blank = False)
    asciiname = models.CharField(
        verbose_name = _("ASCII name"), max_length = 200, blank = False,
        help_text = _("Name in plain ASCII characters."))

    category = models.ForeignKey(GeoeventCategory)
    date_recorded = models.DateTimeField(blank = False, null = False)

    magnitude = models.FloatField(default = None, null = True, blank = False)
    lat = models.DecimalField(max_digits = 8, decimal_places = 6, blank = False, null = False,
        verbose_name = _("latitude"),
        help_text = _("latitude in decimal degrees."))
    lon = models.DecimalField(max_digits = 9, decimal_places = 6, blank = False, null = False,
        verbose_name = _("longitude"),
        help_text = _("longitude in decimal degrees."))

    #api prooperties:
    source = models.ForeignKey(GeoeventSource)
    uid = models.CharField(max_length = 100, blank = True, null = True,
        verbose_name = _("external UID"),
        help_text = _("Unique identifier for a transaction made through an external service.")
    )

    last_modified = models.DateField(auto_now = True, editable = False)

    class Meta:
        abstract = True
