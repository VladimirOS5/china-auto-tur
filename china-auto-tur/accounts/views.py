from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from orders.models import Order


def login_view(request):
    # вход по логину и паролю, при ошибке показываем текст на форме
    error = ""
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect("cabinet")
        error = "Неверный логин или пароль"
    return render(request, "login.html", {"error": error})


def logout_view(request):
    # выход и возврат на главную
    logout(request)
    return redirect("home")


def register_view(request):
    # простая регистрация: логин, пароль два раза, сразу входим
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        p1 = request.POST.get("password1", "")
        p2 = request.POST.get("password2", "")
        if not username or not p1:
            error = "Заполните логин и пароль"
        elif p1 != p2:
            error = "Пароли не совпадают"
        elif User.objects.filter(username=username).exists():
            error = "Такой логин уже занят"
        else:
            user = User.objects.create_user(username, password=p1)
            login(request, user)
            return redirect("cabinet")
    return render(request, "accounts/register.html", {"error": error})


@login_required
def cabinet(request):
    # менеджер и админ видят все заявки и меняют статус, клиент только свои
    manager = (
        request.user.groups.filter(name="managers").exists() or request.user.is_staff
    )
    if request.method == "POST" and manager:
        o = Order.objects.filter(pk=request.POST.get("order_id")).first()
        if o and request.POST.get("status") in dict(Order.STATUS):
            o.status = request.POST["status"]
            o.save()
        return redirect("cabinet")
    orders = Order.objects.all() if manager else Order.objects.filter(user=request.user)
    return render(
        request,
        "cabinet.html",
        {
            "orders": orders.select_related("car"),
            "manager": manager,
            "statuses": Order.STATUS,
        },
    )
