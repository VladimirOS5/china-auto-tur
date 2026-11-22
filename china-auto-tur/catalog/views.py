"""Views каталога: список машин с фильтрами и страница одной машины."""

from django.db import connection
from django.shortcuts import render, get_object_or_404

from .models import Brand, Car


# главная страница каталога: машины справа, бренды слева
def catalog_list(request):
    # основа запроса всегда одна, условия доклеиваем по ходу
    sql = """
        SELECT c.id, c.name, c.year, c.price_cny, c.photo, c.slug,
               c.power, c.battery, c.acceleration,
               b.name_ru AS brand_name, b.id AS brand_id
        FROM catalog_car c
        JOIN catalog_brand b ON b.id = c.brand_id
        WHERE 1 = 1
    """
    params = []

    # бренд приходит кликом из сайдбара, пустую строку фильтром не считаем
    brand_id = request.GET.get("brand", "")
    if brand_id.isdigit():
        sql += " AND b.id = %s"
        params.append(int(brand_id))

    # цену пользователь мог заполнить наполовину, проверяем каждое поле
    price_from = request.GET.get("price_from", "")
    if price_from.isdigit():
        sql += " AND c.price_cny >= %s"
        params.append(int(price_from))

    price_to = request.GET.get("price_to", "")
    if price_to.isdigit():
        sql += " AND c.price_cny <= %s"
        params.append(int(price_to))

    # сортировку берём только из своего списка: чужое значение из адресной строки игнорируем
    sort = request.GET.get("sort", "year_desc")
    order_by = {
        "price_asc": "c.price_cny ASC",
        "price_desc": "c.price_cny DESC",
        "year_desc": "c.year DESC",
        "popularity": "c.id ASC",
    }.get(sort, "c.year DESC")
    sql += " ORDER BY " + order_by

    # значения едут отдельным списком, поэтому инъекций не будет
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [col[0] for col in cur.description]
        cars = [dict(zip(cols, row)) for row in cur.fetchall()]

    brands = Brand.objects.all()

    return render(
        request,
        "catalog/list.html",
        {
            "cars": cars,
            "brands": brands,
            "current_brand": brand_id,
            "current_sort": sort,
        },
    )


# страница одной машины: галерея, панель покупки, табы, похожие
def car_card(request, slug):
    # одну запись проще взять через ORM: получаем объект со всеми его методами
    car = get_object_or_404(Car, slug=slug)

    # похожие для перелинковки: тот же бренд, кроме текущей машины, три штуки
    sql = """
        SELECT c.slug, c.name, c.photo, c.price_cny, b.name_ru AS brand_name
        FROM catalog_car c
        JOIN catalog_brand b ON b.id = c.brand_id
        WHERE c.brand_id = %s AND c.slug <> %s
        ORDER BY c.year DESC
        LIMIT 3
    """
    with connection.cursor() as cur:
        cur.execute(sql, [car.brand_id, car.slug])
        cols = [col[0] for col in cur.description]
        similar = [dict(zip(cols, row)) for row in cur.fetchall()]

    return render(request, "catalog/card.html", {"car": car, "similar": similar})
