# наполнение: бренды и машины из реальных фото, ставки, опции, статьи, пользователи
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from blog.models import Article
from calc.models import Currency, Customs, Fee
from catalog.models import Brand, Car, Purchase, Trim
from orders.models import Option, Order

EXT = (".webp", ".jpg", ".jpeg", ".png")


class Command(BaseCommand):
    help = "Наполняет базу, фото берёт из static/img/cars"

    def handle(self, *args, **options):
        static = Path(settings.BASE_DIR) / "static"
        cars_dir = static / "img" / "cars"
        made = 0
        if cars_dir.exists():
            for i, folder in enumerate(
                sorted(p for p in cars_dir.iterdir() if p.is_dir())
            ):
                files = [f for f in sorted(folder.iterdir()) if f.suffix.lower() in EXT]
                if not files:
                    continue
                brand, _ = Brand.objects.get_or_create(name=folder.name)
                # берём все фото папки, а не первые три: в каталог попадут все машины
                for j, f in enumerate(files):
                    slug = f"{folder.name}-{f.stem}".lower().replace(" ", "-")[:160]
                    if Car.objects.filter(slug=slug).exists():
                        continue
                    car = Car.objects.create(
                        brand=brand,
                        name=f.stem,
                        year=2024 - (j % 3),
                        engine="electric" if j % 3 else "hybrid",
                        power=200 + j * 60,
                        range_km=500 + j * 70,
                        accel=f"{4 + j * 0.4:.1f} с",
                        price_cny=200000 + i * 5000 + j * 20000,
                        photo=f.relative_to(static).as_posix(),
                        slug=slug,
                        description="Авто из Китая под ключ: проверка байером, доставка 30+ дней, гарантия 2 года.",
                    )
                    Trim.objects.create(car=car, name="Comfort", extra_cny=15000)
                    Trim.objects.create(car=car, name="Prestige", extra_cny=45000)
                    made += 1
        if not Car.objects.exists():
            brand, _ = Brand.objects.get_or_create(name="Zeekr")
            Car.objects.create(
                brand=brand, name="001", slug="zeekr-001", price_cny=250000
            )
            made += 1

        for name, price in [
            ("Зимний пакет", 12000),
            ("Ковры премиум", 4000),
            ("Тонировка", 6000),
            ("Сигнализация", 9000),
        ]:
            Option.objects.get_or_create(name=name, defaults={"price_cny": price})

        Currency.objects.get_or_create(code="CNY", defaults={"rate": "12.4000"})
        for engine in ("electric", "hybrid", "petrol"):
            for age, excise, util in (
                ("new", 0 if engine == "electric" else 60, 3400),
                ("used3_5", 0 if engine == "electric" else 120, 5200),
                ("used5", 0 if engine == "electric" else 200, 5200),
            ):
                Customs.objects.get_or_create(
                    engine=engine,
                    age=age,
                    defaults={"duty": 15, "excise": excise, "vat": 20, "util": util},
                )
        for name, amount in [
            ("Логистика до Москвы", 180000),
            ("Таможенное оформление", 60000),
            ("Комиссия компании", 90000),
        ]:
            Fee.objects.get_or_create(name=name, defaults={"amount": amount})

        Article.objects.get_or_create(
            slug="poshlina-2026",
            defaults={
                "title": "Как рассчитать пошлину на авто из Китая в 2026 году",
                "lead": "Пошлина, акциз, НДС и утильсбор по шагам, с примером.",
                "body": "<p>Цена в Китае — половина бюджета.</p>"
                '<h2 id="parts">Из чего состоит платёж</h2>'
                "<p>Пошлина от стоимости, акциз от мощности, НДС от суммы, утильсбор по категории.</p>"
                '<div class="note">Ставки меняются: расчёт фиксируется в договоре.</div>'
                '<h2 id="where">Готовый расчёт</h2>'
                '<p>Откройте <a href="/catalog/">каталог автомобилей из Китая</a>.</p>',
            },
        )
        Article.objects.get_or_create(
            slug="proverka-pered-otpravkoy",
            defaults={
                "title": "Как мы проверяем авто перед отправкой",
                "lead": "Чек-лист байера: кузов, салон, пробег, документы.",
                "body": "<p>Каждую машину до выкупа осматривает байер.</p>"
                '<h2 id="body">Кузов</h2><p>Толщиномер, зазоры, маркировка стёкол.</p>'
                '<h2 id="docs">Документы</h2><p>VIN, сервисная история, экспорт.</p>'
                '<div class="note">Нет осмотра — нет покупки.</div>',
            },
        )

        # менеджер: видит все заявки и меняет статусы
        group, _ = Group.objects.get_or_create(name="managers")
        if not User.objects.filter(username="manager").exists():
            m = User.objects.create_user("manager", password="manager12345")
            m.groups.add(group)
        # клиент: видит только свои заявки
        if not User.objects.filter(username="client").exists():
            u = User.objects.create_user("client", password="client12345")
            car = Car.objects.first()
            if car:
                Order.objects.create(
                    car=car,
                    user=u,
                    name="Клиент",
                    phone="+79000000000",
                    total_cny=car.price_cny,
                )
        # байер: кабинет закупок, плюс одна демо-закупка для проверки
        buyers, _ = Group.objects.get_or_create(name="buyers")
        if not User.objects.filter(username="buyer").exists():
            b = User.objects.create_user("buyer", password="buyer12345")
            b.groups.add(buyers)
            first_car = Car.objects.first()
            if first_car:
                Purchase.objects.create(
                    car=first_car,
                    buyer=b,
                    status="found",
                    note="Демо-закупка для проверки кабинета байера.",
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: добавлено {made}, всего машин {Car.objects.count()}"
            )
        )
