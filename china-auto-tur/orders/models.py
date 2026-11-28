from django.conf import settings
from django.db import models

from catalog.models import Car, Trim, Option


class Order(models.Model):
    STATUS = [("new", "Новая"), ("calc", "Расчёт"), ("contract", "Договор"),
              ("buy", "Выкуп"), ("ship", "Логистика"), ("customs", "Таможня"),
              ("done", "Выдана"), ("cancel", "Отменена")]
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="orders")
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True)
    options = models.ManyToManyField(Option, blank=True)
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField(blank=True)
    city = models.CharField("Город", max_length=60, blank=True)
    comment = models.TextField(blank=True)
    total_cny = models.DecimalField("Итог, юани", max_digits=14, decimal_places=2, default=0)
    status = models.CharField("Статус", max_length=20, choices=STATUS, default="new")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"Заявка #{self.pk} {self.name}"
