from django.db import models


class Message(models.Model):
    KIND = [("feedback", "Обратная связь"), ("callback", "Обратный звонок"),
            ("request", "Заявка на подбор")]
    kind = models.CharField(max_length=20, choices=KIND, default="feedback")
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.get_kind_display()} {self.phone}"
