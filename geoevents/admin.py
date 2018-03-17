#geoevents/admin.py

#django:
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.db import connection

#literati:
from literati.admin_base import NotableAdminBase, SettingsAdminMixin
from literati.utils.formatting import short_datetime_format

#literati_geonames:
from literati_geonames.filters_base import AdminDivisionFilter

#geoevents:
from geoevents.models_base import GeoeventCategory, GeoeventSource
from geoevents.models import Geoevent
from geoevents.filters import (
    ParentGeoeventFilter,
    GeoeventCategoryFilter,
    GeoeventSourceFilter,
    GeoeventMagnitudeFilter,
)
from geoevents.admin_forms import GeoeventForm, GeoeventSettingsForm
from geoevents.admin_modules import (
    GeoeventMagnitudeModule, HourModule,
)

@admin.register(GeoeventCategory)
class GeoeventCategoryAdmin(NotableAdminBase):
    readonly_fields = ("last_modified",)
    list_display = (
        "codename", "name", "is_active", "last_modified", "notes" 
    )
    fields = (
        "name", "codename", "description", "is_active", "last_modified", "notes")
    list_filter = (
        "is_active", "last_modified",
    )
    search_fields = (
        "id", "^name", 
    )
    date_hierarchy = "last_modified"

@admin.register(GeoeventSource)
class GeoeventSourceAdmin(NotableAdminBase):
    list_display = (
        "name", "is_active", "notes" 
    )
    fieldsets = (
        (None, {
            "fields" : (
                "name", "description", "is_active", "details_url", "notes"),
        }),
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "id", "^name", 
    )

@admin.register(Geoevent)
class GeoeventAdmin(SettingsAdminMixin, NotableAdminBase):
    readonly_fields = (
        "last_modified", "get_date_recorded", "get_magnitude",
    )
    fieldsets = (
        (None, {
            "fields" : (
                "name", "asciiname", "category",
            ),
        }),
        (None, {
            "fields" : (
                "date_recorded",
                "magnitude", "admin",
                ("location_search", "lat", "lon"),
            )
        }),
        (None, {
            "fields" : (
                "source", "uid",
            )
        }),
        (None, {
            "fields" : (
                "notes", "last_modified"
            )
        })
    )
    date_hierarchy = "date_recorded"
    search_fields = ('^asciiname', '^admin__name', 'name') 
    list_filter = (
        ParentGeoeventFilter,
        GeoeventCategoryFilter,
        GeoeventSourceFilter,
        GeoeventMagnitudeFilter,
        AdminDivisionFilter,
        "date_recorded",
        "last_modified"
    )
    list_display = (
        'name', 'category', 'get_date_recorded', 'get_magnitude', 
    )
    extra_views = (
        "settings_view",
        "magnitude_view",
        "hour_view",
    )
    tabs = (
        ("Aggregates", {
            "modules" : (
                GeoeventMagnitudeModule,
                HourModule,
            ),
        }),
    )
    form = GeoeventForm

    #settings
    settings_form = GeoeventSettingsForm
    settings_readonly_fields = ("upload_last", )
    settings_fieldsets = (
        ("Upload data", { 
            "fields" : (
                "upload_source", 
                "upload_query_string", 
                "upload_last",
            ),
        }),
    )

    def save_settings(self, request, form):
        result = form.cleaned_data["upload_last_result"]
        msg = _(
            "Data import has been successfully completed. Total time: %(time)s. "
            "Created: %(created)s. Updated: %(updated)s. Errors: %(errors)s."
        ) % result
        self.message_user(request, msg, messages.SUCCESS)
        return super().save_settings(request, form)


    def get_date_recorded(self, obj):
        return short_datetime_format(obj.date_recorded)
    get_date_recorded.short_description = 'date'
    get_date_recorded.admin_order_field = 'date_recorded'

    def get_magnitude(self, obj):

        return format_html('<progress value="{0}" title="{0}" max="10"></progress>', 
            min(10, obj.magnitude) if obj.magnitude else 0)
    get_magnitude.short_description = 'magnitude'
    get_magnitude.admin_order_field = 'magnitude'

    def has_access_magnitudestats_permission(self, request):
        return self._has_permission(request, "access_magnitudestats") 

    def has_access_activity_permission(self, request, obj = None):
        return self._has_permission(request, "access_activity")

    def magnitude_view(self, request):
        if self.has_access_magnitudestats_permission(request):
            cl = self.get_cl(request)
            queryset = cl.get_queryset(request)

            if queryset.exists():
                #raise Exception(str(queryset.query))
                with connection.cursor() as cursor:
                    cursor.execute("""
                        WITH ranges AS (SELECT (factor)::text||'-'||(CASE WHEN factor < 6 THEN factor + 1 ELSE 10 END)::text AS range,
                            factor AS min, CASE WHEN factor < 6 THEN factor + 1 ELSE 10 END AS max
                            FROM generate_series(0,6) AS t(factor))
                        SELECT r.range, count(event.*), sum(event.magnitude), sum(EXTRACT(HOUR FROM event.date_recorded))*60 + sum(EXTRACT(MINUTE FROM event.date_recorded))
                        FROM ranges r
                        LEFT JOIN (%s) event ON event.magnitude >= r.min AND event.magnitude < r.max
                        GROUP BY r.range
                        ORDER BY r.range
                    """ % str(queryset.query))
                    data = { "results" : cursor.fetchall() }
            else:
                errors = ErrorList()
                errors.append(ValidationError(
                    "No %(name)s found for the selected query." % { 
                        "name" : self.opts.verbose_name_plural },
                    code = ErrorCode.INFO,
                ))
                data = { "errors" : errors.get_json_data() }
        else:
            errors = ErrorList()
            errors.append(ValidationError(
                "Need permission to view current occupancy results",
                code = ErrorCode.WARNING,
            ))
            data = { "errors" : errors.get_json_data() }
        return JsonResponse(data)
    magnitude_view.url_pattern = r'^magnitude-data/$'
    magnitude_view.url_name = 'magnitudedata'

    def hour_view(self, request):
        if self.has_access_activity_permission(request):
            cl = self.get_cl(request)
            queryset = cl.get_queryset(request)
            queryset = queryset.extra(
                select = { "hour" : "EXTRACT(hour from date_recorded)::INTEGER" },
            ).values("hour").annotate(count = Count("id")).order_by()
            data = { 
                "results" : list(queryset), 
            }
        else:
            errors = ErrorList()
            errors.append(ValidationError(
                "Need permission to view activity results",
                code = ErrorCode.WARNING,
            ))
            data = { "errors" : errors.get_json_data() }
        return JsonResponse(data)
    hour_view.url_pattern = r'^hour-data/$'
    hour_view.url_name = 'hourdata'
