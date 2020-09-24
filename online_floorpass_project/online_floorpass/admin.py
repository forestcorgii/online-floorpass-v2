from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Department)
admin.site.register(models.Location)
admin.site.register(models.FloorPass)
admin.site.register(models.Log)
admin.site.register(models.User)
admin.site.register(models.GuardManager)
