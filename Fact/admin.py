from django.contrib import admin
from Fact import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
# Register your models here.


class DecadeBornListFilter(admin.SimpleListFilter):
    title = _('decade born')
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        return (
            ('empty', _('Did\'nt have photos')),
            ('had', _('Had photo')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'empty':
            return queryset.filter(image__exact="")
        if self.value() == 'had':
            return queryset.filter(~Q(image__exact=""))


class ObjectAdmin(admin.ModelAdmin):
    date_hierarchy = 'pub_date'
    list_filter = (DecadeBornListFilter, 'category')
    search_fields = ['name']


admin.site.register(models.Member)
admin.site.register(models.Category)
admin.site.register(models.Object, ObjectAdmin)
admin.site.register(models.Fact)
admin.site.register(models.Comment)
admin.site.register(models.Confirm)
