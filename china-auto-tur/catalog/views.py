from django.shortcuts import render
from django.db import connection
from .models import Brand


# Главная страница каталога: список брендов слева, машины справа
def catalog_list(request):
    # бренды для сайдбара — простой запрос через ORM
    brands = Brand.objects.all()

    # пока машин нет, передаём пустой список
    cars = []

    context = {
        "brands": brands,
        "cars": cars,
    }
    return render(request, "catalog/list.html", context)
