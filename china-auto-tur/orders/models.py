from django.conf import settings
from django.db import models
from catalog.models import Car


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Клиент (аккаунт)'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Выбранный автомобиль'
    )
    customer_name = models.CharField(max_length=150, verbose_name='Имя клиента')
    phone = models.CharField(max_length=20, verbose_name='Телефон для связи')
    comment = models.TextField(blank=True, verbose_name='Пожелания по авто / комплектации')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус заявки'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        car_title = self.car if self.car else 'Индивидуальный подбор'
        return f'Заявка №{self.pk} — {car_title} ({self.customer_name})'