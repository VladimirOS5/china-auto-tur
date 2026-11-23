"""Создаёт рабочий проект china-auto-tur целиком: код, окружение, база, данные, запуск."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {}

FILES["manage.py"] = """
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
"""

FILES["config/__init__.py"] = ""
FILES["config/wsgi.py"] = """
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
"""
FILES["config/asgi.py"] = """
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
"""

FILES["config/settings.py"] = """
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'china-auto-tur-local-dev-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
"""

FILES["config/urls.py"] = """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
handler404 = 'core.views.not_found'
"""

FILES["core/__init__.py"] = ""
FILES["core/migrations/__init__.py"] = ""
FILES["core/management/__init__.py"] = ""
FILES["core/management/commands/__init__.py"] = ""

FILES["core/apps.py"] = """
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Каталог и заявки'
"""

FILES["core/models.py"] = """
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField('Бренд', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):
    ENGINE = [('electric', 'Электро'), ('hybrid', 'Гибрид'), ('petrol', 'Бензин')]
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars', verbose_name='Бренд')
    name = models.CharField('Модель', max_length=100)
    year = models.PositiveIntegerField('Год', default=2024)
    engine = models.CharField('Двигатель', max_length=20, choices=ENGINE, default='electric')
    power = models.PositiveIntegerField('Мощность, л.с.', default=200)
    range_km = models.PositiveIntegerField('Запас хода, км', default=600)
    accel = models.CharField('Разгон 0-100', max_length=20, default='5.0 с')
    price_cny = models.DecimalField('Цена, юани', max_digits=12, decimal_places=2, default=250000)
    photo = models.CharField('Фото (путь от static)', max_length=255, blank=True)
    slug = models.SlugField('Адрес', max_length=160, unique=True, blank=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-year', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.brand.name}-{self.name}')[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Trim(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='trims')
    name = models.CharField('Комплектация', max_length=100)
    extra_cny = models.DecimalField('Доплата, юани', max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.car.name} {self.name}'


class Option(models.Model):
    name = models.CharField('Опция', max_length=100)
    price_cny = models.DecimalField('Цена, юани', max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = [('new', 'Новая'), ('calc', 'Расчёт'), ('contract', 'Договор'),
              ('buy', 'Выкуп'), ('ship', 'Логистика'), ('customs', 'Таможня'),
              ('done', 'Выдана'), ('cancel', 'Отменена')]
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='orders')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    trim = models.ForeignKey(Trim, on_delete=models.SET_NULL, null=True, blank=True)
    options = models.ManyToManyField(Option, blank=True)
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField(blank=True)
    city = models.CharField('Город', max_length=60, blank=True)
    comment = models.TextField(blank=True)
    total_cny = models.DecimalField('Итог, юани', max_digits=14, decimal_places=2, default=0)
    status = models.CharField('Статус', max_length=20, choices=STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка #{self.pk} {self.name}'


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    lead = models.TextField('Лид', blank=True)
    body = models.TextField('Текст HTML')
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published']

    def __str__(self):
        return self.title


class Message(models.Model):
    KIND = [('feedback', 'Обратная связь'), ('callback', 'Обратный звонок'), ('request', 'Заявка на подбор')]
    kind = models.CharField(max_length=20, choices=KIND, default='feedback')
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.get_kind_display()} {self.phone}'


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True, default='CNY')
    rate = models.DecimalField('Рублей за единицу', max_digits=10, decimal_places=4, default=12.4)

    def __str__(self):
        return f'{self.code} {self.rate}'


class Customs(models.Model):
    engine = models.CharField(max_length=20)
    age = models.CharField(max_length=20)
    duty = models.DecimalField('Пошлина %', max_digits=5, decimal_places=2, default=15)
    excise = models.DecimalField('Акциз руб/л.с.', max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField('НДС %', max_digits=5, decimal_places=2, default=20)
    util = models.DecimalField('Утильсбор руб', max_digits=12, decimal_places=2, default=3400)

    class Meta:
        unique_together = ['engine', 'age']

    def __str__(self):
        return f'{self.engine} {self.age}'


class Fee(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField('Рубли', max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name
"""

FILES["core/calc.py"] = '''
"""Расчёт под ключ и кредита: только Decimal, округление до рубля."""
from decimal import Decimal, ROUND_HALF_UP


def rub(value):
    return Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def turnkey(price_cny, rate, power, row, fees):
    price = rub(Decimal(price_cny) * rate)
    duty = rub(price * row.duty / 100)
    excise = rub(Decimal(power) * row.excise)
    vat = rub((price + duty + excise) * row.vat / 100)
    util = rub(row.util)
    extra = rub(sum((f.amount for f in fees), Decimal('0')))
    total = price + duty + excise + vat + util + extra
    return dict(price=price, duty=duty, excise=excise, vat=vat, util=util, extra=extra, total=total)


def credit(total, down_pct, months, annual):
    down = rub(total * Decimal(down_pct) / 100)
    body = total - down
    r = Decimal(annual) / 12 / 100
    n = int(months)
    if r == 0:
        pay = rub(body / n)
    else:
        k = (1 + r) ** n
        pay = rub(body * r * k / (k - 1))
    rows = []
    rest = body
    paid = Decimal('0')
    for m in range(1, n + 1):
        pct = rub(rest * r)
        if m == n:
            main = rest
            p = main + pct
        else:
            p = pay
            main = p - pct
        rest -= main
        paid += p
        rows.append([m, p, pct, main, max(rest, Decimal('0'))])
    return dict(down=down, body=body, pay=pay, over=rub(paid - body), rows=rows)
'''

FILES["core/views.py"] = '''
import re
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import calc
from .models import (Brand, Car, Trim, Option, Order, Article, Message,
                     Currency, Customs, Fee)


def digits_ok(phone):
    d = ''.join(c for c in phone if c.isdigit())
    return len(d) == 11 and d[0] in '78'


def home(request):
    return render(request, 'home.html', {
        'brands': Brand.objects.all()[:8],
        'cars': Car.objects.all()[:3],
        'articles': Article.objects.all()[:3],
        'sent': request.GET.get('sent') == '1',
    })


def catalog(request):
    # динамический SQL: условия доклеиваем по выбранным фильтрам
    sql = """SELECT c.id, c.name, c.year, c.price_cny, c.photo, c.slug, c.power,
                    c.range_km, c.accel, b.name AS brand
             FROM core_car c JOIN core_brand b ON b.id = c.brand_id WHERE 1=1"""
    params = []
    brand = request.GET.get('brand', '')
    if brand.isdigit():
        sql += ' AND b.id = %s'
        params.append(int(brand))
    low = request.GET.get('low', '')
    if low.isdigit():
        sql += ' AND c.price_cny >= %s'
        params.append(int(low))
    high = request.GET.get('high', '')
    if high.isdigit():
        sql += ' AND c.price_cny <= %s'
        params.append(int(high))
    sort = request.GET.get('sort', 'year')
    sql += ' ORDER BY ' + {'price_up': 'c.price_cny ASC',
                           'price_down': 'c.price_cny DESC',
                           'year': 'c.year DESC'}.get(sort, 'c.year DESC')
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        cars = [dict(zip(cols, row)) for row in cur.fetchall()]
    return render(request, 'catalog.html', {
        'cars': cars, 'brands': Brand.objects.all(),
        'brand': brand, 'low': low, 'high': high, 'sort': sort,
    })


def car_page(request, slug):
    car = get_object_or_404(Car, slug=slug)
    similar = Car.objects.filter(brand=car.brand).exclude(pk=car.pk)[:3]
    return render(request, 'car.html', {'car': car, 'similar': similar})


def order_page(request):
    car = get_object_or_404(Car, slug=request.GET.get('car', ''))
    trims = list(car.trims.all())
    options = list(Option.objects.all())
    errors, form = {}, {}
    if request.method == 'POST':
        form = request.POST
        name = form.get('name', '').strip()
        phone = form.get('phone', '').strip()
        if not name:
            errors['name'] = 'Напишите имя'
        if not digits_ok(phone):
            errors['phone'] = 'Телефон в формате +7 и 10 цифр'
        if not form.get('consent'):
            errors['consent'] = 'Нужно согласие на обработку данных'
        if not errors:
            total = car.price_cny
            trim = None
            tid = form.get('trim', '')
            if tid.isdigit():
                trim = next((t for t in trims if t.pk == int(tid)), None)
                if trim:
                    total += trim.extra_cny
            chosen = [o for o in options if str(o.pk) in form.getlist('options')]
            for o in chosen:
                total += o.price_cny
            order = Order.objects.create(
                car=car, trim=trim, name=name, phone=phone,
                email=form.get('email', ''), city=form.get('city', ''),
                comment=form.get('comment', ''), total_cny=total,
                user=request.user if request.user.is_authenticated else None)
            order.options.set(chosen)
            return redirect('success')
    return render(request, 'order.html', {
        'car': car, 'trims': trims, 'options': options, 'errors': errors, 'form': form})


def success(request):
    return render(request, 'success.html')


@require_POST
def callback(request):
    phone = request.POST.get('phone', '').strip()
    if digits_ok(phone):
        Message.objects.create(kind='callback', phone=phone)
        return redirect(reverse('home') + '?sent=1')
    return redirect('home')


@require_POST
def quick(request):
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    if not name or not digits_ok(phone) or not request.POST.get('consent'):
        return JsonResponse({'ok': False, 'error': 'Проверьте имя, телефон и согласие'}, status=400)
    Message.objects.create(kind='request', name=name, phone=phone,
                           text=request.POST.get('comment', ''))
    return JsonResponse({'ok': True})


def _calc_params(request):
    def num(key, default):
        try:
            return Decimal(request.GET.get(key, default))
        except (InvalidOperation, TypeError):
            return Decimal(default)
    engine = request.GET.get('engine', 'electric')
    age = request.GET.get('age', 'new')
    if engine not in ('electric', 'hybrid', 'petrol'):
        engine = 'electric'
    if age not in ('new', 'used3_5', 'used5'):
        age = 'new'
    return dict(price=num('price', '250000'), power=int(num('power', '200')),
                engine=engine, age=age, down=num('down', '20'),
                months=int(num('months', '36')), annual=num('annual', '14'))


def calculator(request):
    p = _calc_params(request)
    row = Customs.objects.filter(engine=p['engine'], age=p['age']).first()
    cur = Currency.objects.filter(code='CNY').first()
    fees = list(Fee.objects.all())
    result = credit = None
    if row and cur:
        result = calc.turnkey(p['price'], cur.rate, p['power'], row, fees)
        credit = calc.credit(result['total'], p['down'], p['months'], p['annual'])
    return render(request, 'calc.html', {
        'cars': Car.objects.all(), 'p': p, 'cur': cur, 'fees': fees,
        'r': result, 'c': credit})


def calc_api(request):
    p = _calc_params(request)
    row = Customs.objects.filter(engine=p['engine'], age=p['age']).first()
    cur = Currency.objects.filter(code='CNY').first()
    if not row or not cur:
        return JsonResponse({'ok': False}, status=400)
    r = calc.turnkey(p['price'], cur.rate, p['power'], row, list(Fee.objects.all()))
    c = calc.credit(r['total'], p['down'], p['months'], p['annual'])
    return JsonResponse({'ok': True,
                         'r': {k: str(v) for k, v in r.items()},
                         'c': {'down': str(c['down']), 'pay': str(c['pay']),
                               'over': str(c['over']),
                               'rows': [[str(x) for x in row_] for row_ in c['rows']]}})


def news(request):
    return render(request, 'news.html', {'articles': Article.objects.all()})


def article(request, slug):
    a = get_object_or_404(Article, slug=slug)
    anchors = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', a.body)
    others = Article.objects.exclude(pk=a.pk)[:3]
    return render(request, 'article.html', {'a': a, 'anchors': anchors, 'others': others})


def about(request):
    return render(request, 'about.html')


def contacts(request):
    errors, form = {}, {}
    if request.method == 'POST':
        form = request.POST
        if not form.get('name', '').strip():
            errors['name'] = 'Напишите имя'
        if not digits_ok(form.get('phone', '')):
            errors['phone'] = 'Телефон в формате +7 и 10 цифр'
        if not form.get('consent'):
            errors['consent'] = 'Нужно согласие'
        if not errors:
            Message.objects.create(kind='feedback', name=form['name'],
                                   phone=form['phone'], text=form.get('text', ''))
            return redirect(reverse('contacts') + '?sent=1')
    return render(request, 'contacts.html',
                  {'errors': errors, 'form': form, 'sent': request.GET.get('sent') == '1'})


def policy(request):
    return render(request, 'policy.html')


def login_view(request):
    error = ''
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username', ''),
                            password=request.POST.get('password', ''))
        if user:
            login(request, user)
            return redirect('cabinet')
        error = 'Неверный логин или пароль'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def cabinet(request):
    manager = request.user.groups.filter(name='managers').exists() or request.user.is_staff
    if request.method == 'POST' and manager:
        o = Order.objects.filter(pk=request.POST.get('order_id')).first()
        if o and request.POST.get('status') in dict(Order.STATUS):
            o.status = request.POST['status']
            o.save()
        return redirect('cabinet')
    orders = Order.objects.all() if manager else Order.objects.filter(user=request.user)
    return render(request, 'cabinet.html',
                  {'orders': orders.select_related('car'), 'manager': manager,
                   'statuses': Order.STATUS})


def not_found(request, exception=None):
    return render(request, '404.html', status=404)


def robots(request):
    base = f'{request.scheme}://{request.get_host()}'
    return render(request, 'robots.txt', {'base': base}, content_type='text/plain')


def sitemap(request):
    base = f'{request.scheme}://{request.get_host()}'
    return render(request, 'sitemap.xml',
                  {'base': base, 'cars': Car.objects.all(), 'articles': Article.objects.all()},
                  content_type='application/xml')
'''

FILES["core/urls.py"] = """
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<slug:slug>/', views.car_page, name='car'),
    path('order/', views.order_page, name='order'),
    path('order/success/', views.success, name='success'),
    path('callback/', views.callback, name='callback'),
    path('quick/', views.quick, name='quick'),
    path('calc/', views.calculator, name='calc'),
    path('calc/api/', views.calc_api, name='calc_api'),
    path('news/', views.news, name='news'),
    path('news/<slug:slug>/', views.article, name='article'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('policy/', views.policy, name='policy'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('robots.txt', views.robots, name='robots'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
]
"""

FILES["core/admin.py"] = """
from django.contrib import admin
from .models import (Brand, Car, Trim, Option, Order, Article, Message,
                     Currency, Customs, Fee)

for model in (Brand, Car, Trim, Option, Order, Article, Message, Currency, Customs, Fee):
    admin.site.register(model)
"""

FILES["core/management/commands/seed.py"] = '''
"""Наполнение: бренды и машины из реальных фото, ставки, опции, статьи, пользователи."""
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from core.models import (Brand, Car, Trim, Option, Currency, Customs, Fee,
                         Article, Order)

EXT = ('.webp', '.jpg', '.jpeg', '.png')


class Command(BaseCommand):
    help = 'Наполняет базу данными, фото берёт из static/img/cars'

    def handle(self, *args, **options):
        static = Path(settings.BASE_DIR) / 'static'
        cars_dir = static / 'img' / 'cars'
        made = 0
        if cars_dir.exists():
            for i, folder in enumerate(sorted(p for p in cars_dir.iterdir() if p.is_dir())):
                files = [f for f in sorted(folder.iterdir()) if f.suffix.lower() in EXT]
                if not files:
                    continue
                brand, _ = Brand.objects.get_or_create(name=folder.name)
                for j, f in enumerate(files[:3]):
                    slug = f'{folder.name}-{f.stem}'.lower().replace(' ', '-')[:160]
                    if Car.objects.filter(slug=slug).exists():
                        continue
                    car = Car.objects.create(
                        brand=brand, name=f.stem, year=2024 - (j % 3),
                        engine='electric' if j % 3 else 'hybrid',
                        power=200 + j * 60, range_km=500 + j * 70,
                        accel=f'{4 + j * 0.4:.1f} с',
                        price_cny=200000 + i * 5000 + j * 20000,
                        photo=f.relative_to(static).as_posix(), slug=slug,
                        description='Автомобиль из Китая под ключ: проверка байером, доставка 30+ дней, гарантия 2 года.')
                    Trim.objects.create(car=car, name='Comfort', extra_cny=15000)
                    Trim.objects.create(car=car, name='Prestige', extra_cny=45000)
                    made += 1
        if not Car.objects.exists():
            brand, _ = Brand.objects.get_or_create(name='Zeekr')
            Car.objects.create(brand=brand, name='001', slug='zeekr-001', price_cny=250000)
            made += 1

        for name, price in [('Зимний пакет', 12000), ('Ковры премиум', 4000),
                            ('Тонировка', 6000), ('Сигнализация', 9000)]:
            Option.objects.get_or_create(name=name, defaults={'price_cny': price})

        Currency.objects.get_or_create(code='CNY', defaults={'rate': '12.4000'})
        for engine in ('electric', 'hybrid', 'petrol'):
            for age, excise, util in (('new', 0 if engine == 'electric' else 60, 3400),
                                      ('used3_5', 0 if engine == 'electric' else 120, 5200),
                                      ('used5', 0 if engine == 'electric' else 200, 5200)):
                Customs.objects.get_or_create(engine=engine, age=age,
                                              defaults={'duty': 15, 'excise': excise,
                                                        'vat': 20, 'util': util})
        for name, amount in [('Логистика до Москвы', 180000),
                             ('Таможенное оформление', 60000),
                             ('Комиссия компании', 90000)]:
            Fee.objects.get_or_create(name=name, defaults={'amount': amount})

        Article.objects.get_or_create(
            slug='poshlina-2026',
            defaults={'title': 'Как рассчитать пошлину на авто из Китая в 2026 году',
                      'lead': 'Пошлина, акциз, НДС и утильсбор по шагам, с примером расчёта.',
                      'body': '<p>Цена в Китае — половина бюджета. Вторая половина: платежи и логистика.</p>'
                              '<h2 id="parts">Из чего состоит платёж</h2>'
                              '<p>Пошлина от стоимости, акциз от мощности, НДС от суммы, утильсбор по категории.</p>'
                              '<div class="note">Ставки меняются: расчёт фиксируется в договоре на дату оплаты.</div>'
                              '<h2 id="where">Готовый расчёт</h2>'
                              '<p>Откройте <a href="/catalog/">каталог автомобилей из Китая</a> и запросите расчёт под ключ.</p>'})
        Article.objects.get_or_create(
            slug='proverka-pered-otpravkoy',
            defaults={'title': 'Как мы проверяем авто перед отправкой',
                      'lead': 'Чек-лист байера: кузов, салон, пробег, документы, видеоотчёт.',
                      'body': '<p>Каждую машину до выкупа осматривает байер на месте.</p>'
                              '<h2 id="body">Кузов</h2><p>Толщиномер, зазоры, маркировка стёкол.</p>'
                              '<h2 id="docs">Документы</h2><p>VIN, сервисная история, экспортные papers.</p>'
                              '<div class="note">Нет осмотра — нет покупки, даже если цена вкусная.</div>'})

        group, _ = Group.objects.get_or_create(name='managers')
        if not User.objects.filter(username='manager').exists():
            m = User.objects.create_user('manager', password='manager12345')
            m.groups.add(group)
        if not User.objects.filter(username='client').exists():
            u = User.objects.create_user('client', password='client12345')
            car = Car.objects.first()
            if car:
                Order.objects.create(car=car, user=u, name='Клиент', phone='+79000000000',
                                     total_cny=car.price_cny)
        self.stdout.write(self.style.SUCCESS(f'Готово: машин {made}, всего в базе {Car.objects.count()}'))
'''

FILES["templates/base.html"] = """
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}Авто из Китая под ключ china-auto-tur{% endblock %}</title>
<meta name="description" content="{% block desc %}Подбор, выкуп и доставка автомобилей из Китая под ключ за 30 дней. Цена известна до оплаты.{% endblock %}">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
<div class="topbar"><div class="wrap"><span>Пн–Вс 9:00–21:00 МСК</span><a href="tel:+74950000000">+7 (495) 000-00-00</a></div></div>
<header class="header"><div class="wrap">
  <a class="logo" href="/">CHINA<span>AUTO</span>TUR</a>
  <nav class="nav">
    <a href="/catalog/">Каталог</a><a href="/calc/">Расчёт</a><a href="/news/">Новости</a>
    <a href="/about/">О компании</a><a href="/contacts/">Контакты</a>
  </nav>
  <div class="acts">
    {% if user.is_authenticated %}<a class="user" href="/cabinet/">{{ user.username }}</a><a href="/logout/">Выйти</a>
    {% else %}<a href="/login/">Войти</a>{% endif %}
    <button class="btn red" data-open="req">Заказать авто</button>
    <button class="burger" id="burger" aria-label="Меню"><i></i><i></i><i></i></button>
  </div>
</div></header>
<div class="mobmenu" id="mobmenu">
  <a href="/">Главная</a><a href="/catalog/">Каталог</a><a href="/calc/">Расчёт</a>
  <a href="/news/">Новости</a><a href="/about/">О компании</a><a href="/contacts/">Контакты</a>
  <a href="/cabinet/">Кабинет</a>
</div>
<main>{% block content %}{% endblock %}</main>
<footer class="footer"><div class="wrap">
  <div><span class="logo">CHINA<span>AUTO</span>TUR</span>
    <p>Подбор, выкуп и доставка авто из Китая под ключ. Цена и сроки — в договоре.</p>
    <div class="soc"><a href="https://t.me/chinaautotur">TG</a><a href="https://wa.me/74950000000">WA</a><a href="https://vk.com/chinaautotur">VK</a><a href="https://youtube.com/@chinaautotur">YT</a></div>
  </div>
  <div><b>Меню</b><a href="/catalog/">Каталог</a><a href="/calc/">Расчёт под ключ</a><a href="/news/">Новости</a><a href="/about/">О компании</a></div>
  <div><b>Контакты</b><a href="tel:+74950000000">+7 (495) 000-00-00</a><a href="mailto:hello@china-auto-tur.ru">hello@china-auto-tur.ru</a><span>Москва, Пресненская наб. 12</span></div>
</div><div class="wrap bottom"><span>© 2026 China Auto Tur</span><a href="/policy/">Политика конфиденциальности</a></div></footer>

<div class="modal" id="modal-req"><div class="box">
  <button class="x" data-close>×</button>
  <h3>Заявка на подбор</h3>
  <form id="reqform" method="post" action="/quick/">{% csrf_token %}
    <label>Имя</label><input name="name">
    <label>Телефон</label><input name="phone" placeholder="+7 ___ ___ __ __">
    <label>Комментарий</label><textarea name="comment" rows="3"></textarea>
    <label class="chk"><input type="checkbox" name="consent"><span>Согласен на обработку данных, <a href="/policy/">политика</a></span></label>
    <button class="btn red wide">Отправить заявку</button>
  </form>
</div></div>
<div class="modal" id="modal-ok"><div class="box small"><div class="circle ok">✓</div><h3>Заявка отправлена</h3><p>Менеджер перезвонит в течение 15 минут.</p><button class="btn" data-close>Хорошо</button></div></div>
<div class="modal" id="modal-err"><div class="box small"><div class="circle err">!</div><h3>Не отправилось</h3><p id="errtext">Проверьте поля формы.</p><button class="btn" data-close>Закрыть</button></div></div>
<script src="{% static 'js/main.js' %}"></script>
</body>
</html>
"""

FILES["templates/home.html"] = """
{% extends 'base.html' %}{% load static %}
{% block content %}
<section class="hero"><div class="wrap grid2">
  <div>
    <span class="badge">Импорт авто из Китая</span>
    <h1>Автомобили из Китая под ключ</h1>
    <p class="lead">Подбор, выкуп, таможня и доставка за 30 дней. Цена под ключ известна до оплаты.</p>
    <div class="row"><button class="btn fire" data-open="req">Подобрать авто</button><a class="btn ghost" href="/catalog/">Смотреть каталог</a></div>
    <div class="stats"><div><b>500+</b><span>авто доставлено</span></div><div><b>6 лет</b><span>на рынке</span></div><div><b>30+</b><span>дней доставка</span></div><div><b>98%</b><span>довольных</span></div></div>
  </div>
  {% if cars.0.photo %}<img class="heroimg" src="{% static cars.0.photo %}" alt="Авто из Китая под ключ">{% endif %}
</div></section>

<section class="sec"><div class="wrap">
  <h2>Бренды, с которыми мы работаем</h2>
  <div class="brands">{% for b in brands %}<a class="tile" href="/catalog/?brand={{ b.id }}"><b>{{ b.name }}</b><span>{{ b.cars.count }} моделей</span></a>{% endfor %}</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="head"><h2>Популярные авто</h2><a class="link" href="/catalog/">Каталог автомобилей из Китая →</a></div>
  <div class="cards">{% for car in cars %}{% include 'card.html' %}{% endfor %}</div>
</div></section>

<section class="sec dark"><div class="wrap">
  <h2>Как мы работаем</h2>
  <div class="steps">
    <div class="step"><i>01</i><h3>Заявка</h3><p>Обсуждаем бюджет и пожелания.</p></div>
    <div class="step"><i>02</i><h3>Подбор</h3><p>Проверяем историю и состояние.</p></div>
    <div class="step"><i>03</i><h3>Договор</h3><p>Фиксируем цену и сроки.</p></div>
    <div class="step"><i>04</i><h3>Доставка</h3><p>Таможня и передача ключей.</p></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="head"><h2>Новости</h2><a class="link" href="/news/">Новости об авто из Китая →</a></div>
  <div class="cards">{% for a in articles %}<a class="news" href="/news/{{ a.slug }}/"><div class="cover"></div><time>{{ a.published|date:"d.m.Y" }}</time><h3>{{ a.title }}</h3></a>{% endfor %}</div>
</div></section>

<section class="sec"><div class="wrap cta">
  <div><span class="badge">Бесплатная консультация</span><h2>Нужна помощь с выбором?</h2><p>Оставьте номер — перезвоним за 15 минут.</p></div>
  <form method="post" action="/callback/">{% csrf_token %}
    {% if sent %}<p class="ok-msg">Спасибо! Менеджер перезвонит.</p>{% endif %}
    <div class="row"><input name="phone" placeholder="+7 ___ ___ __ __"><button class="btn">Перезвоните мне</button></div>
    <p class="note">Нажимая кнопку, вы соглашаетесь с <a href="/policy/">политикой</a>.</p>
  </form>
</div></section>
{% endblock %}
"""

FILES["templates/card.html"] = """
{% load static %}
<a class="card" href="/catalog/{{ car.slug }}/">
  {% if car.photo %}<img src="{% static car.photo %}" alt="{{ car.brand }} {{ car.name }}" loading="lazy">
  {% else %}<div class="noimg">Фото скоро появится</div>{% endif %}
  <div class="body">
    <span class="brand">{% firstof car.brand car.brand.name %}</span>
    <h3>{{ car.name }}</h3>
    <div class="specs"><div><span>Мощность</span><b>{{ car.power }} л.с.</b></div><div><span>Запас</span><b>{{ car.range_km }} км</b></div><div><span>Разгон</span><b>{{ car.accel }}</b></div></div>
    <div class="foot"><span>{{ car.year }} год</span><b class="price">{{ car.price_cny|floatformat:0 }} ¥</b></div>
  </div>
</a>
"""

FILES["templates/catalog.html"] = """
{% extends 'base.html' %}
{% block title %}Каталог автомобилей из Китая цены и комплектации{% endblock %}
{% block content %}
<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <span>Каталог</span></nav>
  <h1>Каталог автомобилей из Китая</h1>
  <p class="muted">Найдено {{ cars|length }}</p>
  <div class="layout">
    <aside class="filters">
      <form method="get">
        <label>Бренд</label>
        <select name="brand"><option value="">Все бренды</option>{% for b in brands %}<option value="{{ b.id }}" {% if brand == b.id|stringformat:"i" %}selected{% endif %}>{{ b.name }}</option>{% endfor %}</select>
        <label>Цена от, ¥</label><input name="low" value="{{ low }}" type="number">
        <label>Цена до, ¥</label><input name="high" value="{{ high }}" type="number">
        <label>Сортировка</label>
        <select name="sort"><option value="year" {% if sort == "year" %}selected{% endif %}>Сначала новые</option><option value="price_up" {% if sort == "price_up" %}selected{% endif %}>Дешевле</option><option value="price_down" {% if sort == "price_down" %}selected{% endif %}>Дороже</option></select>
        <button class="btn wide">Применить</button>
        <a class="btn ghost wide" href="/catalog/">Сбросить</a>
      </form>
    </aside>
    <div>
      <div class="cards">{% for car in cars %}{% include 'card.html' %}{% empty %}<p class="muted">По фильтру ничего нет. <a class="link" href="/catalog/">Сбросить фильтры</a></p>{% endfor %}</div>
    </div>
  </div>
</div></section>
{% endblock %}
"""

FILES["templates/car.html"] = """
{% extends 'base.html' %}{% load static %}
{% block title %}{{ car.brand.name }} {{ car.name }} купить из Китая цена и комплектации{% endblock %}
{% block content %}
<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <a href="/catalog/">Каталог</a> / <a href="/catalog/?brand={{ car.brand_id }}">{{ car.brand.name }}</a> / <span>{{ car.name }}</span></nav>
  <div class="carlayout">
    <div>{% if car.photo %}<img class="bigphoto" src="{% static car.photo %}" alt="{{ car.brand.name }} {{ car.name }}">{% else %}<div class="bigphoto noimg">Фото скоро появится</div>{% endif %}</div>
    <aside class="buy">
      <span class="brand">{{ car.brand.name }} · {{ car.year }}</span>
      <h1>{{ car.name }}</h1>
      <p class="bigprice">{{ car.price_cny|floatformat:0 }} ¥</p>
      <a class="btn fire wide" href="/order/?car={{ car.slug }}">Заказать</a>
      <table class="kv">
        <tr><td>Двигатель</td><td>{{ car.get_engine_display }}</td></tr>
        <tr><td>Мощность</td><td>{{ car.power }} л.с.</td></tr>
        <tr><td>Запас хода</td><td>{{ car.range_km }} км</td></tr>
        <tr><td>Разгон</td><td>{{ car.accel }}</td></tr>
        <tr><td>Год</td><td>{{ car.year }}</td></tr>
      </table>
    </aside>
  </div>
  <h2>Обзор {{ car.brand.name }} {{ car.name }}</h2>
  <p class="muted">{{ car.description|default:"Описание появится позже." }}</p>
  <h2>Доставка под ключ</h2>
  <p class="muted">Выкуп, осмотр байером, логистика, таможня и передача ключей за 30+ дней. Цена под ключ фиксируется в договоре.</p>
  {% if similar %}<h2>Похожие автомобили</h2><div class="cards">{% for car in similar %}{% include 'card.html' %}{% endfor %}</div>{% endif %}
</div></section>
{% endblock %}
"""

FILES["templates/order.html"] = """
{% extends 'base.html' %}{% load static %}
{% block title %}Заказ автомобиля из Китая заявка и расчёт под ключ{% endblock %}
{% block content %}
<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <a href="/catalog/">Каталог</a> / <span>Заказ</span></nav>
  <h1>Оформление заказа</h1>
  <div class="progress"><span class="done">1 Авто</span><span class="active">2 Контакты</span><span>3 Подтверждение</span></div>
  <form method="post" class="carlayout">{% csrf_token %}
    <aside class="buy">
      <div class="mini">{% if car.photo %}<img src="{% static car.photo %}" alt="{{ car.name }}">{% endif %}<div><h3>{{ car.brand.name }} {{ car.name }}</h3><b>{{ car.price_cny|floatformat:0 }} ¥</b></div></div>
      <label>Комплектация</label>
      <select name="trim" id="trim" data-base="{{ car.price_cny }}"><option value="0" data-extra="0">Базовая</option>{% for t in trims %}<option value="{{ t.id }}" data-extra="{{ t.extra_cny }}">{{ t.name }} +{{ t.extra_cny|floatformat:0 }} ¥</option>{% endfor %}</select>
      <label>Опции</label>
      {% for o in options %}<label class="chk"><input type="checkbox" name="options" value="{{ o.id }}" data-price="{{ o.price_cny }}"><span>{{ o.name }} +{{ o.price_cny|floatformat:0 }} ¥</span></label>{% endfor %}
      <div class="total"><span>Итого</span><b id="total">{{ car.price_cny|floatformat:0 }} ¥</b></div>
    </aside>
    <div class="form">
      <label>Имя</label><input name="name" value="{{ form.name }}">{% if errors.name %}<p class="err">{{ errors.name }}</p>{% endif %}
      <label>Телефон</label><input name="phone" value="{{ form.phone }}" placeholder="+7 ___ ___ __ __">{% if errors.phone %}<p class="err">{{ errors.phone }}</p>{% endif %}
      <label>Email</label><input name="email" type="email" value="{{ form.email }}">
      <label>Город</label><input name="city" value="{{ form.city }}">
      <label>Комментарий</label><textarea name="comment" rows="4">{{ form.comment }}</textarea>
      <label class="chk"><input type="checkbox" name="consent"><span>Согласен на обработку данных, <a href="/policy/">политика</a></span></label>
      {% if errors.consent %}<p class="err">{{ errors.consent }}</p>{% endif %}
      <button class="btn wide">Отправить заявку</button>
    </div>
  </form>
</div></section>
{% endblock %}
"""

FILES["templates/success.html"] = """
{% extends 'base.html' %}
{% block content %}<section class="sec"><div class="wrap center">
  <div class="circle ok big">✓</div><h1>Заявка отправлена</h1>
  <p class="muted">Менеджер перезвонит в течение 15 минут и пришлёт расчёт под ключ.</p>
  <a class="btn" href="/catalog/">Вернуться в каталог</a>
</div></section>{% endblock %}
"""

FILES["templates/calc.html"] = """
{% extends 'base.html' %}
{% block title %}Калькулятор стоимости авто из Китая расчёт цены под ключ{% endblock %}
{% block content %}
<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <span>Расчёт под ключ</span></nav>
  <h1>Расчёт стоимости под ключ</h1>
  <p class="lead">Меняйте поля — расчёт обновляется сразу. Курс 1 ¥ = {{ cur.rate }} ₽.</p>
  <div class="carlayout">
    <form class="buy" id="cf" onsubmit="return false">
      <label>Машина из каталога</label>
      <select id="pick"><option value="">Свой вариант</option>{% for c in cars %}<option data-price="{{ c.price_cny }}" data-power="{{ c.power }}" data-engine="{{ c.engine }}">{{ c.brand.name }} {{ c.name }}</option>{% endfor %}</select>
      <label>Цена, ¥</label><input type="number" name="price" id="price" value="{{ p.price|floatformat:0 }}">
      <label>Мощность, л.с.</label><input type="number" name="power" id="power" value="{{ p.power }}">
      <label>Двигатель</label><select name="engine" id="engine"><option value="electric" {% if p.engine == "electric" %}selected{% endif %}>Электро</option><option value="hybrid" {% if p.engine == "hybrid" %}selected{% endif %}>Гибрид</option><option value="petrol" {% if p.engine == "petrol" %}selected{% endif %}>Бензин</option></select>
      <label>Возраст</label><select name="age"><option value="new" {% if p.age == "new" %}selected{% endif %}>До 3 лет</option><option value="used3_5" {% if p.age == "used3_5" %}selected{% endif %}>3–5 лет</option><option value="used5" {% if p.age == "used5" %}selected{% endif %}>Старше 5</option></select>
      <label>Первый взнос <b id="dl">{{ p.down|floatformat:0 }}%</b></label><input type="range" name="down" min="0" max="60" step="5" value="{{ p.down|floatformat:0 }}">
      <label>Срок <b id="ml">{{ p.months }} мес</b></label><input type="range" name="months" min="6" max="84" step="6" value="{{ p.months }}">
      <label>Ставка <b id="al">{{ p.annual|floatformat:1 }}%</b></label><input type="range" name="annual" min="5" max="25" step="0.5" value="{{ p.annual|floatformat:1 }}">
      <div class="fees">{% for f in fees %}<div><span>{{ f.name }}</span><b>{{ f.amount|floatformat:0 }} ₽</b></div>{% endfor %}</div>
    </form>
    <div class="form">
      <div class="total big"><span>Цена под ключ</span><b id="r_total">{% if r %}{{ r.total|floatformat:0 }} ₽{% else %}—{% endif %}</b></div>
      <table class="kv">
        <tr><td>Цена в Китае, ₽</td><td id="r_price">{% if r %}{{ r.price|floatformat:0 }}{% endif %}</td></tr>
        <tr><td>Пошлина</td><td id="r_duty">{% if r %}{{ r.duty|floatformat:0 }}{% endif %}</td></tr>
        <tr><td>Акциз</td><td id="r_excise">{% if r %}{{ r.excise|floatformat:0 }}{% endif %}</td></tr>
        <tr><td>НДС</td><td id="r_vat">{% if r %}{{ r.vat|floatformat:0 }}{% endif %}</td></tr>
        <tr><td>Утильсбор</td><td id="r_util">{% if r %}{{ r.util|floatformat:0 }}{% endif %}</td></tr>
        <tr><td>Логистика и комиссия</td><td id="r_extra">{% if r %}{{ r.extra|floatformat:0 }}{% endif %}</td></tr>
      </table>
      <div class="tiles">
        <div><span>Платёж в месяц</span><b id="c_pay">{% if c %}{{ c.pay|floatformat:0 }} ₽{% endif %}</b></div>
        <div><span>Первый взнос</span><b id="c_down">{% if c %}{{ c.down|floatformat:0 }} ₽{% endif %}</b></div>
        <div><span>Переплата</span><b id="c_over" class="warn">{% if c %}{{ c.over|floatformat:0 }} ₽{% endif %}</b></div>
      </div>
      <button class="btn ghost" id="stoggle" type="button">Показать график платежей</button>
      <table class="kv sched" id="sched" hidden><thead><tr><th>Мес</th><th>Платёж</th><th>Проценты</th><th>Тело</th><th>Остаток</th></tr></thead><tbody id="sbody"></tbody></table>
    </div>
  </div>
</div></section>
{% endblock %}
"""

FILES["templates/news.html"] = """
{% extends 'base.html' %}
{% block title %}Блог об авто из Китая статьи и новости china-auto-tur{% endblock %}
{% block content %}<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <span>Новости</span></nav>
  <h1>Новости и статьи об импорте авто</h1>
  <div class="cards">{% for a in articles %}<a class="news" href="/news/{{ a.slug }}/"><div class="cover"></div><time>{{ a.published|date:"d.m.Y" }}</time><h3>{{ a.title }}</h3><p>{{ a.lead|truncatewords:16 }}</p></a>{% endfor %}</div>
</div></section>{% endblock %}
"""

FILES["templates/article.html"] = """
{% extends 'base.html' %}
{% block title %}{{ a.title }}{% endblock %}
{% block desc %}{{ a.lead|truncatewords:24 }}{% endblock %}
{% block content %}<section class="sec"><div class="wrap narrow">
  <nav class="crumbs"><a href="/">Главная</a> / <a href="/news/">Новости</a> / <span>{{ a.title|truncatewords:4 }}</span></nav>
  <h1>{{ a.title }}</h1>
  <p class="muted">{{ a.published|date:"d.m.Y" }}</p>
  <p class="lead">{{ a.lead }}</p>
  {% if anchors %}<nav class="toc"><b>Оглавление</b>{% for id, text in anchors %}<a href="#{{ id }}">{{ text }}</a>{% endfor %}</nav>{% endif %}
  <div class="text">{{ a.body|safe }}</div>
  <div class="cta"><div><h2>Подберём авто под бюджет</h2><p>Расчёт под ключ за 15 минут.</p></div><a class="btn" href="/contacts/">Получить консультацию</a></div>
  {% if others %}<h2>Другие статьи</h2><div class="cards">{% for o in others %}<a class="news" href="/news/{{ o.slug }}/"><div class="cover"></div><h3>{{ o.title }}</h3></a>{% endfor %}</div>{% endif %}
</div></section>{% endblock %}
"""

FILES["templates/about.html"] = """
{% extends 'base.html' %}
{% block title %}О компании china-auto-tur импорт автомобилей из Китая{% endblock %}
{% block content %}
<section class="hero"><div class="wrap"><span class="badge">О компании</span><h1>О компании China Auto Tur</h1><p class="lead">Возим авто из Китая с 2019 года: офис в Москве, свои байеры в Китае, прозрачный расчёт под ключ.</p></div></section>
<section class="sec"><div class="wrap">
  <div class="tiles four"><div><b>500+</b><span>авто доставлено</span></div><div><b>6 лет</b><span>на рынке</span></div><div><b>2</b><span>офиса</span></div><div><b>2 года</b><span>гарантия</span></div></div>
  <h2>Как мы росли</h2>
  <div class="timeline"><div><b>2019</b><p>Первые десять доставок через партнёрские площадки.</p></div><div><b>2021</b><p>Свой офис в Шанхае и штатные байеры.</p></div><div><b>2024</b><p>Пятисотая доставка и калькулятор под ключ.</p></div><div><b>2026</b><p>Гарантия 2 года и кабинет со статусами онлайн.</p></div></div>
  <h2>Почему нам доверяют</h2>
  <div class="steps"><div class="step"><i>✓</i><h3>Проверка до выкупа</h3><p>Видеоотчёт байера до оплаты.</p></div><div class="step"><i>₽</i><h3>Цена заранее</h3><p>Все платежи в договоре.</p></div><div class="step"><i>30</i><h3>Сроки письменно</h3><p>Статус виден в кабинете.</p></div><div class="step"><i>2</i><h3>Гарантия</h3><p>Сервисные партнёры в РФ.</p></div></div>
</div></section>
{% endblock %}
"""

FILES["templates/contacts.html"] = """
{% extends 'base.html' %}
{% block title %}Контакты china-auto-tur офисы в Москве и Китае{% endblock %}
{% block content %}<section class="sec"><div class="wrap">
  <nav class="crumbs"><a href="/">Главная</a> / <span>Контакты</span></nav>
  <h1>Контакты</h1>
  {% if sent %}<p class="ok-msg">Сообщение отправлено, ответим в течение 15 минут.</p>{% endif %}
  <div class="carlayout">
    <div>
      <p class="contact"><span>Телефон</span><a href="tel:+74950000000">+7 (495) 000-00-00</a></p>
      <p class="contact"><span>Почта</span><a href="mailto:hello@china-auto-tur.ru">hello@china-auto-tur.ru</a></p>
      <p class="contact"><span>Режим</span><b>Пн–Вс 9:00–21:00 МСК</b></p>
      <div class="row"><a class="btn ghost" href="https://t.me/chinaautotur">Telegram</a><a class="btn ghost" href="https://wa.me/74950000000">WhatsApp</a><a class="btn ghost" href="https://vk.com/chinaautotur">VK</a></div>
      <div class="branches"><div><h3>Москва</h3><p>Пресненская наб., 12, офис 45</p></div><div><h3>Шанхай</h3><p>Pudong, Century Avenue 100</p></div></div>
    </div>
    <form method="post" class="form">{% csrf_token %}
      <label>Имя</label><input name="name" value="{{ form.name }}">{% if errors.name %}<p class="err">{{ errors.name }}</p>{% endif %}
      <label>Телефон</label><input name="phone" value="{{ form.phone }}">{% if errors.phone %}<p class="err">{{ errors.phone }}</p>{% endif %}
      <label>Сообщение</label><textarea name="text" rows="4">{{ form.text }}</textarea>
      <label class="chk"><input type="checkbox" name="consent"><span>Согласен на обработку данных, <a href="/policy/">политика</a></span></label>
      {% if errors.consent %}<p class="err">{{ errors.consent }}</p>{% endif %}
      <button class="btn">Отправить</button>
    </form>
  </div>
</div></section>{% endblock %}
"""

FILES["templates/policy.html"] = """
{% extends 'base.html' %}
{% block title %}Политика конфиденциальности china-auto-tur{% endblock %}
{% block content %}<section class="sec"><div class="wrap narrow">
  <h1>Политика конфиденциальности</h1>
  <h2>1. Какие данные собираем</h2><p class="muted">Имя, телефон, email и город — только то, что вы оставляете в формах.</p>
  <h2>2. Зачем обрабатываем</h2><p class="muted">Чтобы перезвонить, подготовить расчёт и сопровождать доставку.</p>
  <h2>3. Кому передаём</h2><p class="muted">Сотрудникам, ведущим заявку, и госорганам при оформлении в объёме закона.</p>
  <h2>4. Как храним</h2><p class="muted">В защищённой базе с разграничением прав, три года или до отзыва согласия.</p>
  <h2>5. Ваши права</h2><p class="muted">Запросить копию, исправить или удалить данные, отозвав согласие.</p>
  <h2>6. Контакты</h2><p class="muted">hello@china-auto-tur.ru, ООО «Чайна Авто Тур», Москва, Пресненская наб. 12.</p>
</div></section>{% endblock %}
"""

FILES["templates/login.html"] = """
{% load static %}
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Вход в кабинет</title><link rel="stylesheet" href="{% static 'css/style.css' %}"></head>
<body class="loginpage"><div class="loginbox">
  <a class="logo" href="/">CHINA<span>AUTO</span>TUR</a>
  <h1>Вход в личный кабинет</h1>
  <form method="post">{% csrf_token %}
    <label>Логин</label><input name="username">
    <label>Пароль</label><input type="password" name="password">
    {% if error %}<p class="err">{{ error }}</p>{% endif %}
    <button class="btn wide">Войти</button>
  </form>
  <p class="note">Кабинет создаёт менеджер после первой заявки.</p>
</div></body></html>
"""

FILES["templates/cabinet.html"] = """
{% extends 'base.html' %}
{% block title %}Личный кабинет china-auto-tur{% endblock %}
{% block content %}<section class="sec"><div class="wrap">
  <h1>{% if manager %}Очередь заявок{% else %}Мои заявки{% endif %}</h1>
  <table class="kv table">
    <thead><tr><th>№</th><th>Клиент</th><th>Авто</th><th>Статус</th><th>Сумма</th><th>Дата</th></tr></thead>
    <tbody>
    {% for o in orders %}
      <tr><td>{{ o.id }}</td><td>{{ o.name }}<br><span class="muted">{{ o.phone }}</span></td>
      <td><a class="link" href="/catalog/{{ o.car.slug }}/">{{ o.car.brand.name }} {{ o.car.name }}</a></td>
      <td>{% if manager %}
        <form method="post" class="inline">{% csrf_token %}<input type="hidden" name="order_id" value="{{ o.id }}">
          <select name="status">{% for v, l in statuses %}<option value="{{ v }}" {% if o.status == v %}selected{% endif %}>{{ l }}</option>{% endfor %}</select>
          <button class="btn small">OK</button></form>
        {% else %}<span class="pill">{{ o.get_status_display }}</span>{% endif %}</td>
      <td>{{ o.total_cny|floatformat:0 }} ¥</td><td>{{ o.created|date:"d.m.Y" }}</td></tr>
    {% empty %}<tr><td colspan="6" class="muted">Заявок пока нет</td></tr>{% endfor %}
    </tbody>
  </table>
  <a class="btn" href="/catalog/">Новая заявка</a>
</div></section>{% endblock %}
"""

FILES["templates/404.html"] = """
{% load static %}
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Страница не найдена</title><link rel="stylesheet" href="{% static 'css/style.css' %}"></head>
<body class="lightpage"><div class="errbox"><b>404</b><h1>Страница не найдена</h1>
<p>Возможно, адрес устарел или машину уже выкупили.</p>
<div class="row center"><a class="btn" href="/">На главную</a><a class="btn ghost dark" href="/catalog/">В каталог</a></div></div></body></html>
"""

FILES["templates/robots.txt"] = """User-agent: *
Disallow: /admin/
Disallow: /login/
Disallow: /cabinet/
Disallow: /order/
Disallow: /quick/
Disallow: /callback/
Sitemap: {{ base }}/sitemap.xml
"""

FILES["templates/sitemap.xml"] = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>{{ base }}/</loc></url>
<url><loc>{{ base }}/catalog/</loc></url>
<url><loc>{{ base }}/calc/</loc></url>
<url><loc>{{ base }}/news/</loc></url>
<url><loc>{{ base }}/about/</loc></url>
<url><loc>{{ base }}/contacts/</loc></url>
<url><loc>{{ base }}/policy/</loc></url>
{% for c in cars %}<url><loc>{{ base }}/catalog/{{ c.slug }}/</loc></url>
{% endfor %}{% for a in articles %}<url><loc>{{ base }}/news/{{ a.slug }}/</loc></url>
{% endfor %}</urlset>
"""

FILES["static/css/style.css"] = """
:root{--bg:#0b0b0d;--panel:#15151b;--line:#2a2a33;--txt:#f9fafc;--mut:#a6a6b0;--blue:#4d7cfe;--fire:#ff6a00;--red:#f20530}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--txt);font:16px/1.6 Manrope,Segoe UI,Arial,sans-serif}
a{color:inherit}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.narrow{max-width:820px}
.topbar{background:#08080a;font-size:12px;color:var(--mut)}
.topbar .wrap{display:flex;justify-content:space-between;height:36px;align-items:center}
.topbar a{color:var(--txt);text-decoration:none}
.header{position:sticky;top:0;z-index:50;background:rgba(11,11,13,.95);border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}
.header .wrap{display:flex;align-items:center;justify-content:space-between;height:72px;gap:20px}
.logo{font:700 18px/1 Michroma,Segoe UI,sans-serif;letter-spacing:1px;text-decoration:none}
.logo span{color:var(--blue)}
.nav{display:flex;gap:24px}
.nav a{color:var(--mut);text-decoration:none;font-size:15px}
.nav a:hover{color:var(--blue)}
.acts{display:flex;align-items:center;gap:14px}
.acts a{color:var(--mut);text-decoration:none;font-size:14px}
.btn{display:inline-flex;align-items:center;justify-content:center;height:44px;padding:0 20px;border:0;border-radius:12px;background:var(--blue);color:#fff;font:600 15px Manrope,sans-serif;cursor:pointer;text-decoration:none;transition:.15s}
.btn:hover{filter:brightness(1.12);transform:translateY(-2px)}
.btn.red{background:var(--red)}
.btn.fire{background:linear-gradient(135deg,#ff8a33,#ff4d00);color:#0a0a0c;height:52px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--txt)}
.btn.ghost.dark{border-color:#0b0b0e33;color:#0b0b0e}
.btn.wide{width:100%;margin-top:10px}
.btn.small{height:32px;padding:0 10px;font-size:13px}
.burger{display:none;width:44px;height:44px;background:#1d1d25;border:1px solid var(--line);border-radius:12px;flex-direction:column;gap:4px;align-items:center;justify-content:center;cursor:pointer}
.burger i{width:18px;height:2px;background:var(--txt)}
.mobmenu{display:none;position:fixed;inset:72px 0 0;background:#0b0b0df2;z-index:40;padding:24px;flex-direction:column}
.mobmenu.open{display:flex}
.mobmenu a{padding:16px 0;border-bottom:1px solid var(--line);text-decoration:none;font-size:18px}
.hero{padding:72px 0;background:radial-gradient(1200px 400px at 20% 0%,#1a1a22,#0b0b0d)}
.grid2{display:grid;grid-template-columns:1fr 520px;gap:40px;align-items:center}
.badge{display:inline-block;padding:6px 12px;border-radius:999px;background:#ff6a0022;color:#ff8a33;font:700 12px/1 Manrope;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px}
h1{font:600 44px/1.15 Unbounded,Manrope,sans-serif;margin-bottom:14px}
h2{font:600 26px/1.25 Unbounded,Manrope,sans-serif;margin:28px 0 16px}
h3{font-size:19px}
.lead{color:var(--mut);max-width:560px;margin-bottom:20px}
.row{display:flex;gap:12px;flex-wrap:wrap}
.row.center{justify-content:center}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:32px}
.stats b{display:block;font:600 24px Unbounded,sans-serif}
.stats span{color:var(--mut);font-size:13px}
.heroimg{width:100%;height:420px;object-fit:cover;border-radius:20px}
.sec{padding:48px 0}
.sec.dark{background:#101014}
.head{display:flex;justify-content:space-between;align-items:baseline;gap:16px}
.link{color:var(--blue);text-decoration:none;font-size:14px;font-weight:600}
.brands{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;text-align:center;text-decoration:none;transition:.2s}
.tile:hover{transform:translateY(-4px);border-color:var(--blue)}
.tile b{display:block;font:14px Michroma,sans-serif}
.tile span{color:var(--mut);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden;text-decoration:none;transition:.25s;display:block}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 32px #0007}
.card img{width:100%;height:220px;object-fit:cover;display:block;transition:.4s}
.card:hover img{transform:scale(1.04)}
.noimg{height:220px;display:flex;align-items:center;justify-content:center;background:#1d1d25;color:#6e6e78}
.card .body{padding:18px}
.brand{display:block;font:12px Michroma,sans-serif;color:var(--mut);text-transform:uppercase;margin-bottom:6px}
.specs{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:14px 0;padding:12px 0;border-top:1px solid #ffffff14;border-bottom:1px solid #ffffff14}
.specs span{display:block;color:var(--mut);font-size:12px}
.specs b{font:13px JetBrains Mono,Consolas,monospace}
.foot{display:flex;justify-content:space-between;align-items:center}
.price{font:600 18px Unbounded,sans-serif}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.step{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px}
.step i{display:flex;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#ff8a33,#ff4d00);color:#0a0a0c;font:700 14px/40px Manrope;justify-content:center;margin-bottom:12px;font-style:normal}
.step p{color:var(--mut);font-size:14px}
.news{background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden;text-decoration:none;transition:.25s}
.news:hover{transform:translateY(-4px)}
.cover{height:150px;background:linear-gradient(135deg,#1d1d25,#101014)}
.news time{display:block;color:#6e6e78;font-size:12px;padding:14px 18px 0}
.news h3{padding:6px 18px 16px;font-size:17px}
.news p{padding:0 18px 18px;color:var(--mut);font-size:14px}
.cta{display:grid;grid-template-columns:1fr 460px;gap:32px;background:#101014;border:1px solid var(--line);border-radius:24px;padding:32px;align-items:center}
.cta input,.form input,.form select,.form textarea,.buy input,.buy select,.filters input,.filters select{width:100%;height:46px;background:#16161c;border:1px solid var(--line);border-radius:12px;color:var(--txt);padding:0 14px;font:15px Manrope}
.form textarea,.buy textarea{height:auto;padding:12px 14px}
label{display:block;color:var(--mut);font-size:14px;margin:14px 0 6px}
.chk{display:flex;gap:10px;align-items:flex-start;font-size:13px;color:var(--mut)}
.chk input{width:18px;height:18px;flex:0 0 18px;accent-color:var(--blue)}
.note{color:#6e6e78;font-size:12px;margin-top:10px}
.err{color:#ef4444;font-size:12px;margin-top:6px}
.ok-msg{background:#22c55e22;border:1px solid #22c55e66;color:#22c55e;border-radius:12px;padding:12px;margin-bottom:14px}
.muted{color:var(--mut)}
.crumbs{color:var(--mut);font-size:14px;margin-bottom:18px}
.crumbs a{color:var(--mut);text-decoration:none}
.layout{display:grid;grid-template-columns:280px 1fr;gap:32px;align-items:start}
.filters{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:20px;position:sticky;top:100px}
.carlayout{display:grid;grid-template-columns:1fr 420px;gap:32px;align-items:start}
.bigphoto{width:100%;height:440px;object-fit:cover;border-radius:20px}
.buy{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:22px;position:sticky;top:100px}
.bigprice{font:600 28px Unbounded,sans-serif;margin:10px 0 16px}
.kv{width:100%;border-collapse:collapse;margin-top:14px}
.kv td,.kv th{padding:10px 8px;border-bottom:1px solid #ffffff14;font-size:14px;text-align:left}
.kv td:last-child{text-align:right;font-family:JetBrains Mono,Consolas,monospace}
.table td:last-child{text-align:left}
.mini{display:flex;gap:14px;margin-bottom:12px}
.mini img{width:140px;height:90px;object-fit:cover;border-radius:12px}
.total{display:flex;justify-content:space-between;align-items:baseline;margin-top:18px;padding-top:14px;border-top:1px solid #ffffff14;font:600 20px Unbounded,sans-serif}
.total.big b{color:#ff8a33;font-size:28px}
.progress{display:flex;gap:18px;margin-bottom:24px;color:#6e6e78;font-size:14px}
.progress .done{color:#22c55e}.progress .active{color:var(--txt);font-weight:600}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0}
.tiles.four{grid-template-columns:repeat(4,1fr)}
.tiles div{background:#1d1d25;border:1px solid var(--line);border-radius:14px;padding:14px}
.tiles span{display:block;color:var(--mut);font-size:12px}
.tiles b{font:600 18px Unbounded,sans-serif}
.warn{color:#ffb020}
.fees{margin-top:16px;border-top:1px solid #ffffff14;padding-top:10px}
.fees div{display:flex;justify-content:space-between;font-size:13px;color:var(--mut);padding:4px 0}
input[type=range]{width:100%;accent-color:var(--blue)}
.timeline{border-left:2px solid var(--line);padding-left:24px;display:grid;gap:18px}
.timeline b{color:#ff8a33;font-family:Michroma,sans-serif;font-size:14px}
.timeline p{color:var(--mut)}
.branches{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}
.branches div{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}
.contact{margin-bottom:14px}
.contact span{display:block;color:var(--mut);font-size:13px}
.contact a,.contact b{font-size:17px;font-weight:600;text-decoration:none}
.toc{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;display:grid;gap:8px;margin:20px 0}
.toc a{color:var(--blue);text-decoration:none;font-size:14px}
.text p{color:var(--mut);margin-bottom:14px}
.text h2{scroll-margin-top:90px}
.text .note{background:#4d7cfe1f;border:1px solid #4d7cfe66;border-radius:12px;padding:14px;color:var(--txt);margin:18px 0}
.text a{color:var(--blue)}
.pill{background:#4d7cfe1f;color:var(--blue);border-radius:999px;padding:4px 10px;font-size:12px}
.inline{display:flex;gap:8px;align-items:center}
.inline select{height:34px;background:#16161c;border:1px solid var(--line);border-radius:8px;color:var(--txt)}
.center{text-align:center}
.circle{width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;margin:0 auto 14px}
.circle.big{width:80px;height:80px;font-size:36px}
.circle.ok{background:#22c55e;color:#0a0a0c}
.circle.err{background:#ef4444;color:#fff}
.footer{background:#101014;border-top:1px solid var(--line);padding:40px 0 20px;margin-top:40px}
.footer .wrap{display:grid;grid-template-columns:2fr 1fr 1fr;gap:32px}
.footer p{color:var(--mut);font-size:14px;margin:10px 0}
.footer b{display:block;margin-bottom:8px}
.footer a,.footer span{display:block;color:var(--mut);text-decoration:none;font-size:14px;padding:3px 0}
.footer a:hover{color:var(--blue)}
.soc{display:flex;gap:10px}
.soc a{width:40px;height:40px;border:1px solid var(--line);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:12px}
.bottom{display:flex!important;justify-content:space-between;border-top:1px solid var(--line);margin-top:24px;padding-top:14px;color:#6e6e78;font-size:13px}
.modal{position:fixed;inset:0;background:#050508b8;display:none;align-items:center;justify-content:center;z-index:100;padding:20px}
.modal.open{display:flex}
.box{width:520px;max-height:90vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:28px;position:relative}
.box.small{width:400px;text-align:center}
.box h3{font:600 22px Unbounded,sans-serif;margin-bottom:10px}
.box p{color:var(--mut);font-size:14px;margin-bottom:14px}
.x{position:absolute;top:12px;right:12px;width:36px;height:36px;background:#1d1d25;border:1px solid var(--line);border-radius:10px;color:var(--txt);font-size:20px;cursor:pointer}
.loginpage,.lightpage{min-height:100vh;display:flex;align-items:center;justify-content:center}
.loginpage{background:radial-gradient(800px 400px at 50% 0%,#1a1a22,#0b0b0d)}
.loginbox{width:420px;background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:32px}
.loginbox h1{font-size:24px;margin:14px 0}
.lightpage{background:#f2f2f5;color:#0b0b0e}
.errbox{text-align:center;max-width:560px;padding:32px}
.errbox b{font:700 120px/1 Unbounded,sans-serif;display:block}
.errbox h1{font-size:32px;margin:12px 0}
.errbox p{color:#4a4a52;margin-bottom:20px}
.sched{margin-top:14px}
@media(max-width:1024px){
 .nav{display:none}.burger{display:flex}
 .grid2,.carlayout,.layout,.cta{grid-template-columns:1fr}
 .cards,.steps,.brands,.tiles,.tiles.four{grid-template-columns:repeat(2,1fr)}
 .footer .wrap{grid-template-columns:1fr 1fr}
 .buy,.filters{position:static}
 h1{font-size:32px}
}
@media(max-width:640px){
 .cards,.steps,.brands,.tiles,.tiles.four,.branches,.stats{grid-template-columns:1fr}
 .footer .wrap{grid-template-columns:1fr}
 .acts .btn.red{display:none}
 .heroimg,.bigphoto{height:260px}
}
"""

FILES["static/js/main.js"] = """
// бургер
var burger = document.getElementById('burger'), mob = document.getElementById('mobmenu');
if (burger) burger.onclick = function () { mob.classList.toggle('open'); };

// модалки
function openM(id) { var m = document.getElementById('modal-' + id); if (m) m.classList.add('open'); }
function closeM(m) { m.classList.remove('open'); }
document.querySelectorAll('[data-open]').forEach(function (b) { b.onclick = function () { openM(b.dataset.open); }; });
document.querySelectorAll('.modal').forEach(function (m) {
  m.addEventListener('click', function (e) { if (e.target === m) closeM(m); });
  m.querySelectorAll('[data-close]').forEach(function (b) { b.onclick = function () { closeM(m); }; });
});
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') document.querySelectorAll('.modal.open').forEach(closeM); });

// заявка из модалки
var rf = document.getElementById('reqform');
if (rf) rf.onsubmit = function (e) {
  e.preventDefault();
  var token = rf.querySelector('[name=csrfmiddlewaretoken]').value;
  fetch(rf.action, { method: 'POST', body: new FormData(rf), headers: { 'X-CSRFToken': token } })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      closeM(document.getElementById('modal-req'));
      if (d.ok) { rf.reset(); openM('ok'); }
      else { document.getElementById('errtext').textContent = d.error; openM('err'); }
    })
    .catch(function () { closeM(document.getElementById('modal-req')); openM('err'); });
};

// итог на странице заказа
var trim = document.getElementById('trim');
if (trim) {
  var total = document.getElementById('total');
  var recount = function () {
    var sum = parseFloat(trim.dataset.base) + parseFloat(trim.selectedOptions[0].dataset.extra || 0);
    document.querySelectorAll('input[name=options]:checked').forEach(function (c) { sum += parseFloat(c.dataset.price); });
    total.textContent = Math.round(sum).toLocaleString('ru-RU') + ' ¥';
  };
  document.querySelectorAll('#trim, input[name=options]').forEach(function (el) { el.onchange = recount; });
  recount();
}

// живой калькулятор
var cf = document.getElementById('cf');
if (cf) {
  var fmt = function (v) { return Math.round(parseFloat(v)).toLocaleString('ru-RU'); };
  var t = null;
  var run = function () {
    var p = new URLSearchParams(new FormData(cf));
    fetch('/calc/api/?' + p).then(function (r) { return r.json(); }).then(function (d) {
      if (!d.ok) return;
      document.getElementById('r_total').textContent = fmt(d.r.total) + ' ₽';
      ['price', 'duty', 'excise', 'vat', 'util', 'extra'].forEach(function (k) {
        document.getElementById('r_' + k).textContent = fmt(d.r[k]);
      });
      document.getElementById('c_pay').textContent = fmt(d.c.pay) + ' ₽';
      document.getElementById('c_down').textContent = fmt(d.c.down) + ' ₽';
      document.getElementById('c_over').textContent = fmt(d.c.over) + ' ₽';
      document.getElementById('sbody').innerHTML = d.c.rows.map(function (r) {
        return '<tr><td>' + r[0] + '</td><td>' + fmt(r[1]) + '</td><td>' + fmt(r[2]) + '</td><td>' + fmt(r[3]) + '</td><td>' + fmt(r[4]) + '</td></tr>';
      }).join('');
    });
  };
  cf.addEventListener('input', function (e) {
    if (e.target.name === 'down') document.getElementById('dl').textContent = e.target.value + '%';
    if (e.target.name === 'months') document.getElementById('ml').textContent = e.target.value + ' мес';
    if (e.target.name === 'annual') document.getElementById('al').textContent = e.target.value + '%';
    clearTimeout(t); t = setTimeout(run, 200);
  });
  var pick = document.getElementById('pick');
  pick.onchange = function () {
    var o = pick.selectedOptions[0];
    if (!o.dataset.price) return;
    document.getElementById('price').value = Math.round(parseFloat(o.dataset.price));
    document.getElementById('power').value = o.dataset.power;
    document.getElementById('engine').value = o.dataset.engine;
    run();
  };
  var st = document.getElementById('stoggle'), sc = document.getElementById('sched');
  st.onclick = function () { sc.hidden = !sc.hidden; st.textContent = sc.hidden ? 'Показать график платежей' : 'Скрыть график платежей'; };
  run();
}

// битая картинка -> заглушка
document.addEventListener('error', function (e) {
  var i = e.target;
  if (!i || i.tagName !== 'IMG' || i.dataset.fb) return;
  i.dataset.fb = 1;
  i.src = 'data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="384" height="220"><rect width="384" height="220" fill="#1d1d25"/><path d="M96 140h192l-24-38c-6-9-15-14-26-14h-92c-11 0-20 5-26 14z" fill="#2a2a33"/><circle cx="140" cy="146" r="14" fill="#4d7cfe"/><circle cx="244" cy="146" r="14" fill="#ff6a00"/></svg>');
}, true);
"""


def main():
    print("Пишу файлы проекта...")
    for rel, content in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip("\n") + "\n", encoding="utf-8")
    print("Файлов записано:", len(FILES))

    venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    if not venv_py.exists():
        print("Создаю окружение .venv...")
        subprocess.check_call([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    print("Ставлю Django...")
    subprocess.check_call(
        [str(venv_py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"]
    )
    subprocess.check_call([str(venv_py), "-m", "pip", "install", "--quiet", "django"])

    py = str(venv_py)
    subprocess.check_call([py, "manage.py", "makemigrations", "core"])
    subprocess.check_call([py, "manage.py", "migrate"])
    subprocess.check_call([py, "manage.py", "seed"])

    env = dict(
        os.environ,
        DJANGO_SUPERUSER_USERNAME="admin",
        DJANGO_SUPERUSER_PASSWORD="admin12345",
        DJANGO_SUPERUSER_EMAIL="admin@example.com",
    )
    subprocess.call([py, "manage.py", "createsuperuser", "--noinput"], env=env)

    print("\nГотово. Сайт: http://127.0.0.1:8000/")
    print("Админка: /admin/  логин admin  пароль admin12345")
    print("Менеджер: manager / manager12345   Клиент: client / client12345\n")
    subprocess.call([py, "manage.py", "runserver"])


if __name__ == "__main__":
    main()
