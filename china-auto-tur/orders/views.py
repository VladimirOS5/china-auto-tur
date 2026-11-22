"""Views заявок: страница оформления и приём формы."""

from django.shortcuts import render, get_object_or_404, redirect

from catalog.models import Car, Option
from .models import Order


# страница заказа: слева сводка по машине, справа форма контактов
def order_page(request):
    slug = request.GET.get("car", "")
    car = get_object_or_404(Car, slug=slug)
    trims = car.trims.all()
    options = Option.objects.all()

    # общий набор для шаблона: и при GET, и при возврате формы с ошибками
    context = {
        "car": car,
        "trims": trims,
        "options": options,
        "colors": Order.COLOR_CHOICES,
        "cities": Order.CITY_CHOICES,
        "errors": {},
        "form": {},
        "selected_options": [],
    }

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        city = request.POST.get("city", "moscow")
        comment = request.POST.get("comment", "").strip()
        consent = request.POST.get("consent")
        color = request.POST.get("color", "white")
        trim_id = request.POST.get("trim", "")
        option_ids = request.POST.getlist("options")

        errors = {}
        if not name:
            errors["name"] = "Напишите, как к вам обращаться"
        # телефон проверяем по цифрам: маска может быть любой, цифры обязаны быть
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) != 11 or digits[0] not in "78":
            errors["phone"] = "Телефон в формате +7 и десять цифр"
        if not consent:
            errors["consent"] = "Без согласия на обработку данных заявку не примем"

        if errors:
            # возвращаем форму с ошибками и введёнными данными, чтобы не заполнять заново
            context.update(
                errors=errors, form=request.POST, selected_options=option_ids
            )
            return render(request, "orders/order.html", context)

        # итог считаем на сервере: числу из браузера не верим, его можно подменить
        total = car.price_cny
        trim = None
        if trim_id.isdigit():
            trim = trims.filter(id=int(trim_id)).first()
            if trim:
                total += trim.price_delta
        chosen = options.filter(id__in=[i for i in option_ids if i.isdigit()])
        for opt in chosen:
            total += opt.price_cny

        order = Order.objects.create(
            car=car,
            trim=trim,
            color=color,
            name=name,
            phone=phone,
            email=email,
            city=city,
            comment=comment,
            total_cny=total,
        )
        order.options.set(chosen)
        return redirect("orders:success")

    return render(request, "orders/order.html", context)


# страница успеха после приёма заявки
def order_success(request):
    return render(request, "orders/success.html")
