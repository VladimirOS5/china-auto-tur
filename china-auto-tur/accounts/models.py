"""Профиль пользователя: то, чего нет в стандартном пользователе Django."""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    CITY_CHOICES = [
        ("moscow", "Москва"),
        ("spb", "Санкт-Петербург"),
        ("krasnodar", "Краснодар"),
        ("vladivostok", "Владивосток"),
        ("other", "Другой город"),
    ]

    # один профиль на одного пользователя, удаляется вместе с ним
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)
    city = models.CharField(
        "Город", max_length=20, choices=CITY_CHOICES, default="moscow"
    )

    def __str__(self):
        return f"Профиль {self.user.username}"
