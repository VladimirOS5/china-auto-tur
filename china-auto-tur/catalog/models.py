from django.db import models


# Бренд автомобиля (Zeekr, BYD, Li Auto и так далее)
class Brand(models.Model):
    # сегменты: luxury, premium, middle, mass, economy
    SEGMENT_CHOICES = [
        ("luxury", "Люкс"),
        ("premium", "Премиум"),
        ("middle", "Средний"),
        ("mass", "Масс-маркет"),
        ("economy", "Эконом"),
    ]

    name_ru = models.CharField("Название (рус)", max_length=100)
    name_en = models.CharField("Название (англ)", max_length=100, unique=True)
    segment = models.CharField("Сегмент", max_length=20, choices=SEGMENT_CHOICES)
    country = models.CharField("Страна", max_length=50, default="Китай")
    logo = models.ImageField("Логотип", upload_to="brands/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name_ru"]

    def __str__(self):
        return self.name_ru
