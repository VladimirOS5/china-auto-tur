from django.db import models


class Message(models.Model):
    KIND = [
        ("feedback", "Обратная связь"),
        ("callback", "Обратный звонок"),
        ("request", "Заявка на подбор"),
    ]
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


class HeroSlide(models.Model):
    # слайд главного экрана: админ сам добавляет фото и меняет их порядок
    title = models.CharField("Название", max_length=100, blank=True)
    photo = models.ImageField("Фото авто", upload_to="hero/")
    order = models.PositiveIntegerField("Порядок", default=1)
    active = models.BooleanField("Показывать на сайте", default=True)

    class Meta:
        verbose_name = "Слайд героя"
        verbose_name_plural = "Слайды героя"
        ordering = ["order"]  # сортировка по порядку, заданному админом

    def __str__(self):
        # в админке удобно видеть название или номер слайда
        return self.title or f"Слайд {self.id}"


class HeroSlide(models.Model):
    """Слайд главного экрана: админ сам добавляет фото и меняет порядок."""

    title = models.CharField("Название", max_length=100, blank=True)
    photo = models.ImageField("Фото авто", upload_to="hero/")
    order = models.PositiveIntegerField("Порядок", default=1)
    active = models.BooleanField("Показывать на сайте", default=True)

    class Meta:
        verbose_name = "Слайд героя"
        verbose_name_plural = "Слайды героя"
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Слайд {self.id}"
