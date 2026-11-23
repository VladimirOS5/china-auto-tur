"""Приводит пути картинок в базе к файлам, которые реально лежат в static.
Запускается после clone/pull или после добавления новых фото: битых путей не остаётся.
"""

import os
from itertools import cycle
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from catalog.models import Brand, Car
from blog.models import Article

STATIC = Path(settings.BASE_DIR) / "static"
CARS = STATIC / "img" / "cars"
BRANDS = STATIC / "img" / "brands"
NEWS = STATIC / "img" / "news"
TEXTURES = STATIC / "img" / "textures"
EXT = (".webp", ".jpg", ".jpeg", ".png", ".svg")


def rel(path):
    return path.relative_to(STATIC).as_posix()


def norm(text):
    return "".join(ch for ch in text.lower() if ch.isalnum())


# 1. проверяем фоны: без них сайт живой, но плоский
for name in ("ink-dark.jpg", "ink-light.jpg"):
    p = TEXTURES / name
    print("фон на месте:" if p.exists() else "НЕТ ФОНА, положи файл:", p)

# 2. индекс файлов по брендовым папкам + циклы, чтобы машины не получили одно фото
index = {}
if CARS.exists():
    for d in sorted(CARS.iterdir()):
        if d.is_dir():
            files = [f for f in sorted(d.iterdir()) if f.suffix.lower() in EXT]
            if files:
                index[norm(d.name)] = {"files": files, "cycle": cycle(files)}

# 3. фото машин: существующий путь не трогаем, пустой или битый — чиним
fixed = 0
for car in Car.objects.select_related("brand"):
    if car.photo and (STATIC / car.photo).exists():
        continue
    bucket = index.get(norm(car.brand.name_en)) or index.get(norm(car.brand.name_ru))
    if bucket is None:
        bucket = next(iter(index.values()), None)
    if bucket is None:
        car.photo = ""
        car.save()
        print("нет файлов вообще для:", car)
        continue
    target = norm(car.name)
    match = next(
        (f for f in bucket["files"] if target and target in norm(f.stem)), None
    )
    chosen = match or next(bucket["cycle"])
    car.photo = rel(chosen)
    car.save()
    fixed += 1
    print("фото:", car, "->", car.photo)

# 4. логотипы брендов: ставим путь только если файл действительно есть
for brand in Brand.objects.all():
    if brand.logo and (STATIC / brand.logo).exists():
        continue
    found = (
        next(
            (
                f
                for f in sorted(BRANDS.iterdir())
                if f.suffix.lower() in EXT and norm(f.stem) == norm(brand.name_en)
            ),
            None,
        )
        if BRANDS.exists()
        else None
    )
    brand.logo = rel(found) if found else ""
    brand.save()

# 5. обложки статей: есть файлы — раздаём по кругу, нет — оставляем пусто (шаблон даст заглушку)
news_files = (
    [f for f in sorted(NEWS.iterdir()) if f.suffix.lower() in EXT]
    if NEWS.exists()
    else []
)
if news_files:
    nc = cycle(news_files)
    for article in Article.objects.all():
        if article.cover and (STATIC / article.cover).exists():
            continue
        article.cover = rel(next(nc))
        article.save()

print("готово, исправлено путей фото:", fixed)
