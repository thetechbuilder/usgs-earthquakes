#geoevents/admin_modules.py

#django:
from django.urls import reverse
from django.utils.safestring import mark_safe

#literait:
from literati.admin_modules_base import (
    ModuleAdminBase, 
)
from literati.utils.admin import construct_admin_urlname, ErrorCode

class GeoeventMagnitudeModule(ModuleAdminBase):
    template_name = "admin/geoevents/geoevent/modules/magnitude.html"
    module_title = "magnitude stats"
    module_name = "magnitude-module"

    def get_context_data(self):
        context = super().get_context_data()
        opts = self.opts

        data_url = reverse(construct_admin_urlname(
            opts.app_label, opts.model_name, "magnitudedata"))
        #get query string template for data URL -->
        context.update({
            "change_url" : mark_safe(reverse(construct_admin_urlname(
                self.opts.app_label, self.opts.model_name, "changelist")) + self.query_string),
            "data_url" : mark_safe(data_url + self.query_string),
        })
        return context

    class Media:
        css = {
            "all" : (
                "literati/admin/css/reports.css",
                "geoevents/admin/css/geoevent.css",
            ),
        }
        js = (
            "base/js/vendor/chart/Chart.bundle.js",
            "geoevents/admin/js/geoevent.js",
        )

class HourModule(ModuleAdminBase):
    template_name = "admin/geoevents/geoevent/modules/hour.html"
    module_title = "hour activity"
    module_name = "hour-module"

    def get_context_data(self):
        context = super().get_context_data()
        opts = self.opts

        data_url = reverse(construct_admin_urlname(
            opts.app_label, opts.model_name, "hourdata"))
        #get query string template for data URL -->
        context.update({
            "change_url" : mark_safe(reverse(construct_admin_urlname(
                self.opts.app_label, self.opts.model_name, "changelist")) + self.query_string),
            "data_url" : mark_safe(data_url + self.query_string),
        })
        return context

    class Media:
        css = {
            "all" : (
                "literati/admin/css/reports.css",
                "geoevents/admin/css/geoevent.css",
            ),
        }
        js = (
            "base/js/vendor/chart/Chart.bundle.js",
            "literati/admin/js/basemodules.js",
            "geoevents/admin/js/geoevent.js",
        )

