"""Калькулятор: страница с контролами и JSON-эндпоинт для живого пересчёта."""

from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import Car
from .models import CurrencyRate, CustomsRate, Fee
from . import services


def _num(request, key, default):
    # числа из запроса читаем аккуратно: мусор заменяем значением по умолчанию
    try:
        return Decimal(request.GET.get(key, default))
    except (InvalidOperation, TypeError):
        return Decimal(default)


def _params(request):
    car = Car.objects.order_by("-year").first()
    default_price = str(car.price_cny) if car else "250000"
    default_power = "163"
    if car and car.power:
        digits = "".join(ch for ch in car.power if ch.isdigit())
        if digits:
            default_power = digits

    engine = request.GET.get("engine", "electric")
    age = request.GET.get("age", "new")
    if engine not in dict(CustomsRate.ENGINE_CHOICES):
        engine = "electric"
    if age not in dict(CustomsRate.AGE_CHOICES):
        age = "new"

    return {
        "price_cny": _num(request, "price_cny", default_price),
        "power_hp": _num(request, "power_hp", default_power),
        "engine": engine,
        "age": age,
        "down_percent": _num(request, "down_percent", "20"),
        "months": int(_num(request, "months", "36")),
        "annual_percent": _num(request, "annual_percent", "14"),
    }


def calculator(request):
    p = _params(request)
    rate_row = CustomsRate.objects.filter(engine=p["engine"], age=p["age"]).first()
    currency = CurrencyRate.objects.filter(code="CNY").first()
    fees = list(Fee.objects.all())

    result = None
    credit = None
    if rate_row and currency:
        result = services.turnkey(
            p["price_cny"], currency.rate, p["power_hp"], rate_row, fees
        )
        credit = services.annuity(
            result["total"], p["down_percent"], p["months"], p["annual_percent"]
        )

    return render(
        request,
        "calc/calculator.html",
        {
            "cars": Car.objects.order_by("name"),
            "engines": CustomsRate.ENGINE_CHOICES,
            "ages": CustomsRate.AGE_CHOICES,
            "currency": currency,
            "fees": fees,
            "p": p,
            "result": result,
            "credit": credit,
        },
    )


def calculator_api(request):
    p = _params(request)
    rate_row = CustomsRate.objects.filter(engine=p["engine"], age=p["age"]).first()
    currency = CurrencyRate.objects.filter(code="CNY").first()
    if not rate_row or not currency:
        return JsonResponse({"ok": False, "error": "Ставки не заполнены"}, status=400)

    fees = list(Fee.objects.all())
    result = services.turnkey(
        p["price_cny"], currency.rate, p["power_hp"], rate_row, fees
    )
    credit = services.annuity(
        result["total"], p["down_percent"], p["months"], p["annual_percent"]
    )

    return JsonResponse(
        {
            "ok": True,
            "price_rub": str(result["price_rub"]),
            "duty": str(result["customs"]["duty"]),
            "excise": str(result["customs"]["excise"]),
            "vat": str(result["customs"]["vat"]),
            "util": str(result["customs"]["util"]),
            "customs_total": str(result["customs"]["total"]),
            "fees_total": str(result["fees_total"]),
            "total": str(result["total"]),
            "down": str(credit["down"]),
            "credit_sum": str(credit["credit_sum"]),
            "payment": str(credit["payment"]),
            "overpay": str(credit["overpay"]),
            "schedule": [
                [
                    s["month"],
                    str(s["payment"]),
                    str(s["interest"]),
                    str(s["principal"]),
                    str(s["balance"]),
                ]
                for s in credit["schedule"]
            ],
        }
    )
