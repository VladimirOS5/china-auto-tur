from django.db import connection
from django.shortcuts import render, get_object_or_404

from .models import Brand, Car


def catalog(request):
    # динамический SQL: условия доклеиваем по выбранным фильтрам
    sql = """SELECT c.id, c.name, c.year, c.price_cny, c.photo, c.slug, c.power,
                    c.range_km, c.accel, b.name AS brand
             FROM catalog_car c JOIN catalog_brand b ON b.id = c.brand_id WHERE 1=1"""
    params = []
    brand = request.GET.get("brand", "")
    if brand.isdigit():
        sql += " AND b.id = %s"
        params.append(int(brand))
    low = request.GET.get("low", "")
    if low.isdigit():
        sql += " AND c.price_cny >= %s"
        params.append(int(low))
    high = request.GET.get("high", "")
    if high.isdigit():
        sql += " AND c.price_cny <= %s"
        params.append(int(high))
    sort = request.GET.get("sort", "year")
    sql += " ORDER BY " + {"price_up": "c.price_cny ASC",
                           "price_down": "c.price_cny DESC",
                           "year": "c.year DESC"}.get(sort, "c.year DESC")
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        cars = [dict(zip(cols, row)) for row in cur.fetchall()]
    return render(request, "catalog.html", {
        "cars": cars, "brands": Brand.objects.all(),
        "brand": brand, "low": low, "high": high, "sort": sort})


def car_page(request, slug):
    car = get_object_or_404(Car, slug=slug)
    similar = Car.objects.filter(brand=car.brand).exclude(pk=car.pk)[:3]
    return render(request, "car.html", {"car": car, "similar": similar})
