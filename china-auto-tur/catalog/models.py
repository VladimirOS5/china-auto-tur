from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Brand(models.Model):
    name = models.CharField("Бренд", max_length=100, unique=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Car(models.Model):
    ENGINE = [("electric", "Электро"), ("hybrid", "Гибрид"), ("petrol", "Бензин")]
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="cars", verbose_name="Бренд"
    )
    name = models.CharField("Модель", max_length=100)
    year = models.PositiveIntegerField("Год", default=2024)
    engine = models.CharField(
        "Двигатель", max_length=20, choices=ENGINE, default="electric"
    )
    power = models.PositiveIntegerField("Мощность, л.с.", default=200)
    range_km = models.PositiveIntegerField("Запас хода, км", default=600)
    accel = models.CharField("Разгон 0-100", max_length=20, default="5.0 с")
    price_cny = models.DecimalField(
        "Цена, юани", max_digits=12, decimal_places=2, default=250000
    )
    photo = models.CharField("Фото (путь от static)", max_length=255, blank=True)
    slug = models.SlugField("Адрес", max_length=160, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["-year", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Trim(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="trims")
    name = models.CharField("Комплектация", max_length=100)
    extra_cny = models.DecimalField(
        "Доплата, юани", max_digits=12, decimal_places=2, default=0
    )

    def __str__(self):
        return f"{self.car.name} {self.name}"


class Option(models.Model):
    name = models.CharField("Опция", max_length=100)
    price_cny = models.DecimalField(
        "Цена, юани", max_digits=12, decimal_places=2, default=0
    )

    def __str__(self):
        return self.name


class Purchase(models.Model):
    # закупка машины байером в Китае: от находки до отправки
    STATUS = [
        ("found", "Найдена"),
        ("checked", "Проверена"),
        ("bought", "Выкуплена"),
        ("shipped", "Отправлена"),
    ]
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name="purchases", verbose_name="Машина"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Байер",
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="found")
    price_cny = models.DecimalField(
        "Цена выкупа, юани", max_digits=12, decimal_places=2, default=0
    )
    note = models.TextField("Заметка", blank=True)
    created = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Закупка"
        verbose_name_plural = "Закупки"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.car} — {self.get_status_display()}"
