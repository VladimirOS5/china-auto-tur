from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from orders.models import Order


def login_view(request):
    error = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""),
                            password=request.POST.get("password", ""))
        if user:
            login(request, user)
            return redirect("cabinet")
        error = "Неверный логин или пароль"
    return render(request, "login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def cabinet(request):
    manager = request.user.groups.filter(name="managers").exists() or request.user.is_staff
    if request.method == "POST" and manager:
        o = Order.objects.filter(pk=request.POST.get("order_id")).first()
        if o and request.POST.get("status") in dict(Order.STATUS):
            o.status = request.POST["status"]
            o.save()
        return redirect("cabinet")
    orders = Order.objects.all() if manager else Order.objects.filter(user=request.user)
    return render(request, "cabinet.html", {
        "orders": orders.select_related("car"), "manager": manager,
        "statuses": Order.STATUS})
