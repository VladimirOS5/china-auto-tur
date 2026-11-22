from django.contrib import admin

from .models import Brand, Car, Trim, Option

admin.site.register(Brand)
admin.site.register(Car)
admin.site.register(Trim)
admin.site.register(Option)
