"""Модели заявок: клиент оставляет заявку на конкретную машину."""

from django.conf import settings
from django.db import models

from catalog.models import Car, Trim, Option


class Order(models.Model):
    # статусы из спецификации: путь заявки от новой до выдачи
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("calculation", "Расчёт"),
        ("contract", "Договор"),
        ("deposit", "Предоплата"),
        ("purchase", "Выкуп"),
        ("china", "В Китае"),
        ("logistics", "Логистика"),
        ("customs", "Таможня"),
        ("delivery", "Доставка"),
        ("done", "Выдана"),
        ("cancelled", "Отменена"),
    ]
    CITY_CHOICES = [
        ("moscow", "Москва"),
        ("spb", "Санкт-Петербург"),
        ("krasnodar", "Краснодар"),
        ("vladivostok", "Владивосток"),
        ("other", "Другой город"),
    ]
    COLOR_CHOICES = [
        ("white", "Белый"),
        ("black", "Чёрный"),
        ("silver", "Серебристый"),
        ("blue", "Синий"),
        ("red", "Красный"),
    ]

    # PROTECT: машину с заявками удалить нельзя, история заказов важнее
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Автомобиль",
    )
    trim = models.ForeignKey(
        Trim,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Комплектация",
    )
    options = models.ManyToManyField(Option, blank=True, verbose_name="Опции")
    color = models.CharField(
        "Цвет", max_length=20, choices=COLOR_CHOICES, default="white"
    )

    # заявка может прийти и от гостя: тогда user пустой, а контакты лежат в name/phone
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Клиент",
    )

    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    city = models.CharField(
        "Город", max_length=20, choices=CITY_CHOICES, default="moscow"
    )
    comment = models.TextField("Комментарий", blank=True)

    # итог считаем на сервере при приёме заявки и кладём сюда готовым
    total_cny = models.DecimalField(
        "Итог в юанях", max_digits=12, decimal_places=2, default=0
    )
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="new"
    )
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка #{self.id} — {self.name}"
