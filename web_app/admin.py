from django.contrib import admin

# Register your models here.

from web_app.models import unit,participate,student
admin.site.register(student)
admin.site.register(unit)
admin.site.register(participate)