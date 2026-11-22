from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from .decorators import manager_required, admin_required


def register_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet_client')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('cabinet_client')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('cabinet_client')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_admin_role:
                return redirect('admin_panel')
            if user.is_manager:
                return redirect('cabinet_manager')
            return redirect('cabinet_client')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


@login_required
def cabinet_client_view(request):
    if request.method == 'POST':
        # Берём присланные данные и привязываем к текущему пользователю (instance=request.user)
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Контактные данные успешно обновлены!')
            return redirect('cabinet_client')
    else:
        # При обычном открытии страницы заполняем поля текущими данными пользователя из БД
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/cabinet_client.html', {'form': form})


@manager_required
def cabinet_manager_view(request):
    return render(request, 'accounts/cabinet_manager.html')


@admin_required
def admin_panel_view(request):
    return render(request, 'accounts/admin_panel.html')