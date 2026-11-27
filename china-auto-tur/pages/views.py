from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from blog.models import Article
from catalog.models import Brand, Car
from config.utils import digits_ok
from .models import Message


def home(request):
    return render(request, "home.html", {
        "brands": Brand.objects.all()[:8],
        "cars": Car.objects.all()[:3],
        "articles": Article.objects.all()[:3],
        "sent": request.GET.get("sent") == "1"})


@require_POST
def callback(request):
    phone = request.POST.get("phone", "").strip()
    if digits_ok(phone):
        Message.objects.create(kind="callback", phone=phone)
        return redirect(reverse("home") + "?sent=1")
    return redirect("home")


def about(request):
    return render(request, "about.html")


def contacts(request):
    errors, form = {}, {}
    if request.method == "POST":
        form = request.POST
        if not form.get("name", "").strip():
            errors["name"] = "Напишите имя"
        if not digits_ok(form.get("phone", "")):
            errors["phone"] = "Телефон в формате +7 и 10 цифр"
        if not form.get("consent"):
            errors["consent"] = "Нужно согласие"
        if not errors:
            Message.objects.create(kind="feedback", name=form["name"],
                                   phone=form["phone"], text=form.get("text", ""))
            return redirect(reverse("contacts") + "?sent=1")
    return render(request, "contacts.html", {
        "errors": errors, "form": form, "sent": request.GET.get("sent") == "1"})


def policy(request):
    return render(request, "policy.html")


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def robots(request):
    base = f"{request.scheme}://{request.get_host()}"
    return render(request, "robots.txt", {"base": base}, content_type="text/plain")


def sitemap(request):
    base = f"{request.scheme}://{request.get_host()}"
    return render(request, "sitemap.xml", {
        "base": base, "cars": Car.objects.all(), "articles": Article.objects.all()},
        content_type="application/xml")
