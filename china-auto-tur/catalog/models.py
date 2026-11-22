"""Модели каталога: бренды и автомобили."""

from django.db import models
from django.utils.text import slugify


# Бренд — справочник: по нему работает сайдбар каталога
# и плитки брендов на главной, поэтому вынесен в отдельную таблицу
class Brand(models.Model):
    # сегменты из спецификации: в админке станут выпадающим списком
    SEGMENT_CHOICES = [
        ("luxury", "Люкс"),
        ("premium", "Премиум"),
        ("middle", "Средний"),
        ("mass", "Масс-маркет"),
        ("economy", "Эконом"),
    ]

    name_ru = models.CharField("Название на русском", max_length=100)
    # name_en нужен для URL и надписей Michroma, он только латиницей
    name_en = models.CharField("Название на английском", max_length=100, unique=True)
    segment = models.CharField("Сегмент", max_length=20, choices=SEGMENT_CHOICES)
    country = models.CharField("Страна", max_length=50, default="Китай")

    # логотип лежит в static, поэтому храним путь, а не сам файл:
    # файлы дизайна версионируются в Git, а не грузятся через админку
    logo = models.CharField(
        "Путь к логотипу (static)",
        max_length=255,
        blank=True,
        help_text="Например: img/brands/zeekr.svg",
    )
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name_ru"]

    def __str__(self):
        # в админке и в шаблонах бренд показываем русским названием
        return self.name_ru


# Автомобиль — карточка каталога: одна запись равна одной карточке на сайте
class Car(models.Model):
    ENGINE_CHOICES = [
        ("electric", "Электро"),
        ("hybrid", "Гибрид"),
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
    ]
    DRIVE_CHOICES = [
        ("fwd", "Передний"),
        ("rwd", "Задний"),
        ("awd", "Полный"),
    ]

    # связь с брендом: машины тянут название бренда через JOIN,
    # поэтому имя бренда не дублируется в каждой карточке
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="cars",
        verbose_name="Бренд",
    )
    name = models.CharField("Модель", max_length=100, help_text="Например: 001 FR")
    year = models.PositiveIntegerField("Год выпуска")
    engine = models.CharField(
        "Двигатель", max_length=20, choices=ENGINE_CHOICES, default="electric"
    )
    drive = models.CharField(
        "Привод", max_length=20, choices=DRIVE_CHOICES, default="awd"
    )

    # деньги держим в Decimal: float для цен не используем принципиально
    price_cny = models.DecimalField("Цена в юанях", max_digits=10, decimal_places=2)

    # slug даёт красивый адрес карточки: /catalog/zeekr-001-fr/
    slug = models.SlugField("Адрес страницы", max_length=150, unique=True, blank=True)

    # фото лежит в static/img/cars/Бренд/, храним путь от папки static:
    # например img/cars/Zeekr/zeekr-001-fr.webp
    photo = models.CharField(
        "Путь к фото (static)",
        max_length=255,
        blank=True,
        help_text="Например: img/cars/Zeekr/zeekr-001-fr.webp",
    )

    # три значения для мини-таблицы внутри карточки каталога
    power = models.CharField(
        "Мощность", max_length=50, blank=True, help_text="Например: 163 л.с."
    )
    battery = models.CharField(
        "Запас хода", max_length=50, blank=True, help_text="Например: 656 км"
    )
    acceleration = models.CharField(
        "Разгон 0-100", max_length=50, blank=True, help_text="Например: 3,8 с"
    )

    # текст для вкладки «Обзор» на странице машины
    description = models.TextField(
        "Описание",
        blank=True,
        help_text="Текст для вкладки «Обзор» на странице машины",
    )

    created_at = models.DateTimeField("Добавлен", auto_now_add=True)

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["-year"]  # свежие года показываем первыми

    def save(self, *args, **kwargs):
        # если slug не заполнили руками, собираем его сами из бренда и модели,
        # чтобы не спотыкаться об это поле при каждом добавлении машины
        if not self.slug:
            self.slug = slugify(f"{self.brand.name_en}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name_ru} {self.name}"


# Комплектация: уровень оснащения конкретной машины, доплата к базовой цене
class Trim(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="trims",
        verbose_name="Автомобиль",
    )
    name = models.CharField("Название", max_length=100, help_text="Например: Comfort")
    price_delta = models.DecimalField(
        "Доплата к базе", max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "Комплектация"
        verbose_name_plural = "Комплектации"
        ordering = ["price_delta"]

    def __str__(self):
        return f"{self.car.name} — {self.name}"


# Опция: платная дополнительная штука, общая для всех машин
class Option(models.Model):
    name = models.CharField("Название", max_length=100)
    price_cny = models.DecimalField("Цена", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Опция"
        verbose_name_plural = "Опции"
        ordering = ["name"]

    def __str__(self):
        return self.name
