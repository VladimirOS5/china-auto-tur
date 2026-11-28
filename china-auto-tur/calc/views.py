from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render

from catalog.models import Car
from . import services
from .models import Currency, Customs, Fee


def _params(request):
    def num(key, default):
        try:
            return Decimal(request.GET.get(key, default))
        except (InvalidOperation, TypeError):
            return Decimal(default)
    engine = request.GET.get("engine", "electric")
    age = request.GET.get("age", "new")
    if engine not in ("electric", "hybrid", "petrol"):
        engine = "electric"
    if age not in ("new", "used3_5", "used5"):
        age = "new"
    return dict(price=num("price", "250000"), power=int(num("power", "200")),
                engine=engine, age=age, down=num("down", "20"),
                months=int(num("months", "36")), annual=num("annual", "14"))


def calculator(request):
    p = _params(request)
    row = Customs.objects.filter(engine=p["engine"], age=p["age"]).first()
    cur = Currency.objects.filter(code="CNY").first()
    fees = list(Fee.objects.all())
    r = c = None
    if row and cur:
        r = services.turnkey(p["price"], cur.rate, p["power"], row, fees)
        c = services.credit(r["total"], p["down"], p["months"], p["annual"])
    return render(request, "calc.html", {
        "cars": Car.objects.all(), "p": p, "cur": cur, "fees": fees, "r": r, "c": c})


def calc_api(request):
    p = _params(request)
    row = Customs.objects.filter(engine=p["engine"], age=p["age"]).first()
    cur = Currency.objects.filter(code="CNY").first()
    if not row or not cur:
        return JsonResponse({"ok": False}, status=400)
    r = services.turnkey(p["price"], cur.rate, p["power"], row, list(Fee.objects.all()))
    c = services.credit(r["total"], p["down"], p["months"], p["annual"])
    return JsonResponse({"ok": True,
                         "r": {k: str(v) for k, v in r.items()},
                         "c": {"down": str(c["down"]), "pay": str(c["pay"]),
                               "over": str(c["over"]),
                               "rows": [[str(x) for x in row_] for row_ in c["rows"]]}})
