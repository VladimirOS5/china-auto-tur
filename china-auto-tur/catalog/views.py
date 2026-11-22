from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import manager_required
from .models import Brand, Car
from .forms import CarForm


def car_list_view(request):
    brands = Brand.objects.all()
    if request.user.is_authenticated and request.user.is_manager:
        cars = Car.objects.select_related('brand').all()
    else:
        cars = Car.objects.select_related('brand').filter(is_available=True)

    brand_slug = request.GET.get('brand')
    if brand_slug:
        cars = cars.filter(brand__slug=brand_slug)

    context = {
        'cars': cars,
        'brands': brands,
        'selected_brand': brand_slug,
    }
    return render(request, 'catalog/list.html', context)


def car_detail_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'catalog/card.html', {'car': car})


@manager_required
def car_create_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'Автомобиль {car} добавлен в каталог.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm()

    return render(request, 'catalog/car_form.html', {
        'form': form,
        'title': 'Добавить автомобиль',
    })


@manager_required
def car_edit_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные автомобиля обновлены.')
            return redirect('car_detail', pk=car.pk)
    else:
        form = CarForm(instance=car)

    return render(request, 'catalog/car_form.html', {
        'form': form,
        'title': f'Редактировать: {car}',
    })


@manager_required
def car_delete_view(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Автомобиль удалён из каталога.')
        return redirect('car_list')
    return redirect('car_detail', pk=pk)