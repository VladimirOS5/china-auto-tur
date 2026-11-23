"""Разовое наполнение справочников расчёта: курс, ставки, постоянные расходы."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from calc.models import CurrencyRate, CustomsRate, Fee

# курс учебный,近似 реальному диапазону юаня; правится в админке
CurrencyRate.objects.get_or_create(code="CNY", defaults={"rate": "12.4000"})

# ставки учебные: структура настоящая (пошлина, акциз за л.с., НДС, утильсбор)
rows = [
    ("electric", "new", "15", "0", "20", "3400"),
    ("electric", "used3_5", "15", "0", "20", "3400"),
    ("electric", "used5", "15", "0", "20", "5200"),
    ("hybrid", "new", "15", "60", "20", "3400"),
    ("hybrid", "used3_5", "15", "120", "20", "5200"),
    ("hybrid", "used5", "15", "200", "20", "5200"),
    ("petrol", "new", "15", "60", "20", "3400"),
    ("petrol", "used3_5", "15", "120", "20", "5200"),
    ("petrol", "used5", "15", "200", "20", "5200"),
    ("diesel", "new", "15", "60", "20", "3400"),
    ("diesel", "used3_5", "15", "120", "20", "5200"),
    ("diesel", "used5", "15", "200", "20", "5200"),
]
for engine, age, duty, excise, vat, util in rows:
    CustomsRate.objects.get_or_create(
        engine=engine,
        age=age,
        defaults={
            "duty_percent": duty,
            "excise_per_hp": excise,
            "vat_percent": vat,
            "util_fee": util,
        },
    )

for name, amount in [
    ("Логистика до Москвы", "180000"),
    ("Таможенное оформление", "60000"),
    ("Комиссия компании", "90000"),
]:
    Fee.objects.get_or_create(name=name, defaults={"amount_rub": amount})

print("справочники расчёта заполнены")
