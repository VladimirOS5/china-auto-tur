from django.shortcuts import render
from catalog.models import Car
from blog.models import Post


def home_view(request):
    cars = Car.objects.select_related('brand').filter(is_available=True)[:4]
    posts = Post.objects.filter(is_published=True)[:3]

    return render(request, 'pages/home.html', {
        'cars': cars,
        'posts': posts,
    })


def about_view(request):
    return render(request, 'pages/about.html')


def contacts_view(request):
    return render(request, 'pages/contacts.html')


def policy_view(request):
    return render(request, 'pages/policy.html')