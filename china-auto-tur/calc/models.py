"""Справочники для расчёта: курс валюты, таможенные ставки и постоянные расходы."""

from django.db import models


class CurrencyRate(models.Model):
    code = models.CharField("Валюта", max_length=10, unique=True, default="CNY")
    rate = models.DecimalField("Рублей за единицу", max_digits=10, decimal_places=4)
    updated = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"

    def __str__(self):
        return f"{self.code} = {self.rate} ₽"


class CustomsRate(models.Model):
    ENGINE_CHOICES = [
        ("electric", "Электро"),
        ("hybrid", "Гибрид"),
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
    ]
    AGE_CHOICES = [
        ("new", "До 3 лет"),
        ("used3_5", "3–5 лет"),
        ("used5", "Старше 5 лет"),
    ]

    engine = models.CharField("Двигатель", max_length=20, choices=ENGINE_CHOICES)
    age = models.CharField("Возраст", max_length=20, choices=AGE_CHOICES)
    duty_percent = models.DecimalField("Пошлина, %", max_digits=5, decimal_places=2)
    excise_per_hp = models.DecimalField(
        "Акциз, руб за л.с.", max_digits=10, decimal_places=2
    )
    vat_percent = models.DecimalField("НДС, %", max_digits=5, decimal_places=2)
    util_fee = models.DecimalField("Утильсбор, руб", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Таможенная ставка"
        verbose_name_plural = "Таможенные ставки"
        unique_together = ["engine", "age"]

    def __str__(self):
        return f"{self.get_engine_display()} / {self.get_age_display()}"


class Fee(models.Model):
    # постоянные расходы под ключ: логистика, оформление, комиссия — правятся в админке
    name = models.CharField("Название", max_length=100)
    amount_rub = models.DecimalField("Сумма, руб", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Расход под ключ"
        verbose_name_plural = "Расходы под ключ"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} — {self.amount_rub} ₽"
