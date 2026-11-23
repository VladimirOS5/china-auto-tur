from django.contrib import admin

from .models import CurrencyRate, CustomsRate, Fee

admin.site.register(CurrencyRate)
admin.site.register(CustomsRate)
admin.site.register(Fee)
