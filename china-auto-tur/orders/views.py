from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from catalog.models import Car, Option
from config.utils import digits_ok
from pages.models import Message
from .models import Order


def order_page(request):
    car = get_object_or_404(Car, slug=request.GET.get("car", ""))
    trims = list(car.trims.all())
    options = list(Option.objects.all())
    errors, form = {}, {}
    if request.method == "POST":
        form = request.POST
        name = form.get("name", "").strip()
        phone = form.get("phone", "").strip()
        if not name:
            errors["name"] = "Напишите имя"
        if not digits_ok(phone):
            errors["phone"] = "Телефон в формате +7 и 10 цифр"
        if not form.get("consent"):
            errors["consent"] = "Нужно согласие на обработку данных"
        if not errors:
            total = car.price_cny
            trim = None
            tid = form.get("trim", "")
            if tid.isdigit():
                trim = next((t for t in trims if t.pk == int(tid)), None)
                if trim:
                    total += trim.extra_cny
            chosen = [o for o in options if str(o.pk) in form.getlist("options")]
            for o in chosen:
                total += o.price_cny
            order = Order.objects.create(
                car=car, trim=trim, name=name, phone=phone,
                email=form.get("email", ""), city=form.get("city", ""),
                comment=form.get("comment", ""), total_cny=total,
                user=request.user if request.user.is_authenticated else None)
            order.options.set(chosen)
            return redirect("success")
    return render(request, "order.html", {
        "car": car, "trims": trims, "options": options, "errors": errors, "form": form})


def success(request):
    return render(request, "success.html")


@require_POST
def quick(request):
    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    if not name or not digits_ok(phone) or not request.POST.get("consent"):
        return JsonResponse({"ok": False, "error": "Проверьте имя, телефон и согласие"}, status=400)
    Message.objects.create(kind="request", name=name, phone=phone,
                           text=request.POST.get("comment", ""))
    return JsonResponse({"ok": True})
