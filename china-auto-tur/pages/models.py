"""Сообщения с сайта: обратная связь, заказ обратного звонка и заявка на подбор."""

from django.db import models


class ContactMessage(models.Model):
    KIND_CHOICES = [
        ("feedback", "Обратная связь"),
        ("callback", "Обратный звонок"),
        ("request", "Заявка на подбор"),
    ]

    kind = models.CharField(
        "Тип", max_length=20, choices=KIND_CHOICES, default="feedback"
    )
    name = models.CharField("Имя", max_length=100, blank=True)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} — {self.phone}"
