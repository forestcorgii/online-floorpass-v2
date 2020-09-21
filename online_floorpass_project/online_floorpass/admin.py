from django.contrib import admin

from .models import Department, Location,FloorPass,Log,User

# Register your models here.
admin.site.register(Department)
admin.site.register(Location)
admin.site.register(FloorPass)
admin.site.register(Log)
admin.site.register(User)
