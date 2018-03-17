#geoevents/admin_forms.py
import time
from datetime import timedelta

#django:
from django import forms
from django.utils.translation import gettext as _, gettext_lazy
from django.core.exceptions import ValidationError

#literati:
from literati.forms.forms import AppForm
from literati.forms.widgets import TextInput
from literati.utils.datetime import Calendar

#jqwidgets:
from jqwidgets.forms.widgets import JQSlider, OLSearchWidget

#autocomplete:
from dal import autocomplete

#geoevents:
from geoevents.models import Geoevent
from geoevents.adapters.forms import UPLOAD_ADAPTERS
from geoevents.adapters.exceptions import UploadAdapterException 

class GeoeventSettingsForm(AppForm):

    SOURCE_NONE = 0
    SOURCE_USGS_EARTHQUAKES = 1

    upload_source = forms.ChoiceField(
        label = gettext_lazy("Source"),
        initial = 0,
        choices = (
            (SOURCE_NONE, "-"*8),
            (SOURCE_USGS_EARTHQUAKES, gettext_lazy("USGS Earthquakes")),
        ),
        required = False,
    )
    upload_query_string = forms.CharField(
        label = gettext_lazy("Query string"),
        help_text = gettext_lazy(
            "Query string should be submitted based on the API specifications. "
            "Please consult the API documentation for more details."),
        widget = TextInput(attrs = { "class" : "extended", }), 
        required = False)
    upload_last = forms.DateTimeField(
        label = gettext_lazy("Last uploaded"),
        required = False)

    def clean_upload_source(self):
        return int(self.cleaned_data["upload_source"])

    def clean(self):

        #upload values:
        source = self.cleaned_data.get("upload_source")
        query_string = self.cleaned_data.get("upload_query_string")
        if source and query_string:
            #get upload adaptere
            adapter = UPLOAD_ADAPTERS[source]
            try:
                t1 = time.time()
                result = adapter.upload(query_string)
                t2 = time.time()
            except UploadAdapterException as e:
                self.add_error(None, e)
            except Exception as e:
                self.add_error(None, 
                    ValidationError(_(
                        "Error occured while uploading")))
            else:
                result["time"] = timedelta(seconds = t2 - t1)
                #update upload last value
                self.cleaned_data["upload_last"] = Calendar.get_now()
                self.cleaned_data["upload_last_result"] = result 
            

class GeoeventForm(forms.ModelForm):

    location_search = forms.CharField(
        required = False, label = gettext_lazy("Location search"), 
        widget = OLSearchWidget(attrs = { 
            "title" : gettext_lazy("Use the address fields."),
            "data-bound-latitude" : "id_lat", 
            "data-bound-longitude" : "id_lon",})
    )

    class Meta:
        model = Geoevent
        fields = "__all__"
        widgets = {
            "magnitude" : JQSlider(
                attrs = { "min" : 0, "max" : 10, "step" : 0.01, "size" : 20 }),
            "admin": autocomplete.ModelSelect2(
                url='literati_admin:literati_geonames:admindivision-autocomplete',
                attrs = { 'data-placeholder' : 'ID, Name or Codename...' }),
            "category": autocomplete.ModelSelect2(
                url='literati_admin:geoevents:activegeoeventcategory-autocomplete',
                attrs = { 'data-placeholder' : 'Name...' }),
            "source": autocomplete.ModelSelect2(
                url='literati_admin:geoevents:activegeoeventsource-autocomplete',
                attrs = { 'data-placeholder' : 'Name...' }),
        }
