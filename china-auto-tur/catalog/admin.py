from django.contrib import admin
from .models import Brand, Car


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model_name', 'year', 'price', 'is_available')
    list_filter = ('brand', 'year', 'transmission', 'drive_type', 'is_available')
    search_fields = ('model_name', 'brand__name')
    list_editable = ('price', 'is_available')