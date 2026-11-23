"""Views аккаунтов: вход, выход и кабинеты клиента и менеджера."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from orders.models import Order
from .models import Profile


def is_manager(user):
    # роль смотрим по группе: группы заводим в админке один раз
    return user.groups.filter(name="managers").exists()


def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # без галочки «запомнить» сессия живёт до закрытия браузера
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            # менеджера сразу в очередь, остальных в кабинет клиента
            if is_manager(user):
                return redirect("accounts:manager")
            return redirect("accounts:cabinet")
        error = "Неверный логин или пароль"
    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("catalog:list")


@login_required
def cabinet_client(request):
    # профиль создаём при первом заходе, чтобы не заводить его руками
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # имя и почта живут на пользователе, телефон и город в профиле
        request.user.first_name = request.POST.get("name", "").strip()
        request.user.email = request.POST.get("email", "").strip()
        request.user.save()
        profile.phone = request.POST.get("phone", "").strip()
        profile.city = request.POST.get("city", profile.city)
        profile.save()
        return redirect("accounts:cabinet")

    # клиент видит только свои заявки, чужие сюда не попадают
    orders = Order.objects.filter(user=request.user).select_related("car", "car__brand")
    return render(
        request, "accounts/cabinet_client.html", {"orders": orders, "profile": profile}
    )


@login_required
def cabinet_manager(request):
    if not is_manager(request.user):
        # интерфейс спрячет чужое, но сервер проверяет сам: обойти адресом нельзя
        return redirect("accounts:cabinet")

    if request.method == "POST":
        order = get_object_or_404(Order, id=request.POST.get("order_id"))
        new_status = request.POST.get("status", "")
        # статус берём только из своего списка, чужое значение игнорируем
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
        return redirect("accounts:manager")

    orders = Order.objects.select_related("car", "car__brand").all()

    status = request.GET.get("status", "")
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    search = request.GET.get("q", "").strip()
    if search:
        orders = orders.filter(name__icontains=search)

    return render(
        request,
        "accounts/cabinet_manager.html",
        {
            "orders": orders,
            "statuses": Order.STATUS_CHOICES,
            "current_status": status,
            "q": search,
        },
    )
