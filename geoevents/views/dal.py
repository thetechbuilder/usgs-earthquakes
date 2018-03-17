#geoevents/views/dal.py

#literati:
from literati.views.dal_base import (
    AdminModelAutocompleteBase,
    CategoryBaseAutocompleteBase,
)

#geoevents
from geoevents.models_base import GeoeventCategory, GeoeventSource
from geoevents.models import Geoevent

class GeoeventAutocomplete(AdminModelAutocompleteBase):
    model = Geoevent

    def get_filtered(self, q):
        limit_choices_to = self.get_limit_choices_to()
        return self.model.objects.filter(limit_choices_to & Q(name__icontains = q))

class GeoeventCategoryAutocomplete(CategoryBaseAutocompleteBase):
    model = GeoeventCategory 

class GeoeventSourceAutocomplete(CategoryBaseAutocompleteBase):
    model = GeoeventCategory 
