from django.contrib import admin
from .models import Brand, Car, Trim, Option

for m in (Brand, Car, Trim, Option):
    admin.site.register(m)
