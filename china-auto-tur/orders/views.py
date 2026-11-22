from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import manager_required
from catalog.models import Car
from .models import Order
from .forms import OrderForm


def order_create_view(request):
    initial_data = {}

    car_id = request.GET.get('car')
    if car_id and car_id.isdigit():
        car = Car.objects.filter(pk=car_id).first()
        if car:
            initial_data['car'] = car

    if request.user.is_authenticated:
        full_name = f'{request.user.first_name} {request.user.last_name}'.strip()
        initial_data['customer_name'] = full_name or request.user.username
        if request.user.phone:
            initial_data['phone'] = request.user.phone

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.client = request.user
            order.save()
            messages.success(request, f'Заявка №{order.pk} успешно отправлена! Менеджер свяжется с вами в ближайшее время.')
            if request.user.is_authenticated:
                return redirect('cabinet_client')
            return redirect('home')
    else:
        form = OrderForm(initial=initial_data)

    return render(request, 'orders/order.html', {'form': form})


@manager_required
def order_status_update_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заявки №{order.pk} обновлён.')
    return redirect('cabinet_manager')