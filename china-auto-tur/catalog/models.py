from django.db import models
from django.db import models
from django.templatetags.static import static


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Марка')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL-метка')

    class Meta:
        verbose_name = 'Марка'
        verbose_name_plural = 'Марки'
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):
    TRANSMISSION_CHOICES = (
        ('automatic', 'Автомат (АКПП)'),
        ('robot', 'Робот (DCT)'),
        ('cvt', 'Вариатор (CVT)'),
        ('electric', 'Редуктор (Электро)'),
    )

    DRIVE_CHOICES = (
        ('fwd', 'Передний'),
        ('rwd', 'Задний'),
        ('awd', 'Полный (4WD)'),
    )
    
    static_image = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Фото из каталога (static/img/cars)'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='cars',
        verbose_name='Марка'
    )
    model_name = models.CharField(max_length=150, verbose_name='Модель')
    year = models.PositiveIntegerField(verbose_name='Год выпуска')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Цена (₽)')
    engine_volume = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name='Объём двигателя (л)'
    )
    horsepower = models.PositiveIntegerField(verbose_name='Мощность (л.с.)')
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        default='automatic',
        verbose_name='Коробка передач'
    )
    drive_type = models.CharField(
        max_length=10,
        choices=DRIVE_CHOICES,
        default='fwd',
        verbose_name='Привод'
    )
    image = models.ImageField(
        upload_to='cars/',
        blank=True,
        null=True,
        verbose_name='Фотография'
    )
    description = models.TextField(blank=True, verbose_name='Описание и комплектация')
    is_available = models.BooleanField(default=True, verbose_name='Доступен к заказу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.brand.name} {self.model_name} ({self.year})'
    @property
    def get_image_url(self):
        if self.static_image:
            return static(self.static_image)
        if self.image:
            return self.image.url
        return ''