from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from .decorators import manager_required, admin_required
from orders.models import Order
from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from catalog.models import Car
from blog.models import Post




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
    orders = Order.objects.select_related('car', 'car__brand', 'client').all()
    return render(request, 'accounts/cabinet_manager.html', {'orders': orders})


@admin_required
def admin_panel_view(request):
    stats = {
        'cars_count': Car.objects.count(),
        'orders_count': Order.objects.count(),
        'new_orders_count': Order.objects.filter(status='new').count(),
        'posts_count': Post.objects.count(),
        'users_count': User.objects.count(),
    }
    users = User.objects.all().order_by('-date_joined')
    role_choices = User._meta.get_field('role').choices

    return render(request, 'accounts/admin_panel.html', {
        'stats': stats,
        'users': users,
        'role_choices': role_choices,
    })


@admin_required
def user_role_update_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if target_user == request.user:
            messages.error(request, 'Нельзя изменить роль самому себе.')
            return redirect('admin_panel')

        new_role = request.POST.get('role')
        if new_role in {'client', 'manager', 'admin'}:
            target_user.role = new_role
            target_user.is_staff = (new_role == 'admin')
            target_user.save()
            messages.success(request, f'Роль пользователя {target_user.username} обновлена.')
            
    return redirect('admin_panel')