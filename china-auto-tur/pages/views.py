"""Публичные страницы: главная, о компании, контакты, политика, 404 и SEO-файлы."""

from django.shortcuts import render, redirect
from django.urls import reverse

from catalog.models import Brand, Car
from blog.models import Article
from .models import ContactMessage


def home(request):
    context = {
        "brands": Brand.objects.all()[:6],
        "cars": Car.objects.order_by("-year")[:3],
        "articles": Article.objects.filter(is_published=True)[:3],
        "sent": request.GET.get("sent") == "1",
        "error": request.GET.get("error") == "1",
    }
    return render(request, "pages/home.html", context)


def about(request):
    return render(request, "pages/about.html", {"hero_car": Car.objects.first()})


def contacts(request):
    errors = {}
    form = {}
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        consent = request.POST.get("consent")

        if not name:
            errors["name"] = "Напишите, как к вам обращаться"
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) != 11 or digits[0] not in "78":
            errors["phone"] = "Телефон в формате +7 и десять цифр"
        if not message:
            errors["message"] = "Напишите пару слов, о чём вопрос"
        if not consent:
            errors["consent"] = "Без согласия на обработку данных сообщение не примем"

        if errors:
            form = request.POST
        else:
            ContactMessage.objects.create(
                kind="feedback",
                name=name,
                phone=phone,
                email=email,
                message=message,
            )
            return redirect(reverse("pages:contacts") + "?sent=1")

    return render(
        request,
        "pages/contacts.html",
        {
            "errors": errors,
            "form": form,
            "sent": request.GET.get("sent") == "1",
        },
    )


def callback(request):
    # форма с главной: только телефон, остальное менеджер уточнит по звонку
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) == 11 and digits[0] in "78":
            ContactMessage.objects.create(
                kind="callback", name="Обратный звонок", phone=phone
            )
            return redirect(reverse("pages:home") + "?sent=1")
        return redirect(reverse("pages:home") + "?error=1")
    return redirect("pages:home")


def policy(request):
    return render(request, "pages/policy.html")


def handler404(request, exception):
    return render(request, "pages/404.html", status=404)


def robots_txt(request):
    # служебные страницы закрываем от индексации, карту сайта отдаём сразу
    base = f"{request.scheme}://{request.get_host()}"
    return render(
        request, "seo/robots.txt", {"base_url": base}, content_type="text/plain"
    )


def sitemap_xml(request):
    base = f"{request.scheme}://{request.get_host()}"
    return render(
        request,
        "seo/sitemap.xml",
        {
            "base_url": base,
            "cars": Car.objects.all(),
            "articles": Article.objects.filter(is_published=True),
        },
        content_type="application/xml",
    )
