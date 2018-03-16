from django.contrib import admin
from Fact import models
# Register your models here.


admin.site.register(models.Member)
admin.site.register(models.Category)
admin.site.register(models.Object)
admin.site.register(models.Fact)
admin.site.register(models.Comment)
admin.site.register(models.Confirm)
