from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True, default="CNY")
    rate = models.DecimalField("Рублей за единицу", max_digits=10, decimal_places=4, default=12.4)

    def __str__(self):
        return f"{self.code} {self.rate}"


class Customs(models.Model):
    engine = models.CharField(max_length=20)
    age = models.CharField(max_length=20)
    duty = models.DecimalField("Пошлина %", max_digits=5, decimal_places=2, default=15)
    excise = models.DecimalField("Акциз руб/л.с.", max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField("НДС %", max_digits=5, decimal_places=2, default=20)
    util = models.DecimalField("Утильсбор руб", max_digits=12, decimal_places=2, default=3400)

    class Meta:
        unique_together = ["engine", "age"]

    def __str__(self):
        return f"{self.engine} {self.age}"


class Fee(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField("Рубли", max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name
