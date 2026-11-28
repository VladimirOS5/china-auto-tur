from django.contrib import admin
from .models import Currency, Customs, Fee

for m in (Currency, Customs, Fee):
    admin.site.register(m)
