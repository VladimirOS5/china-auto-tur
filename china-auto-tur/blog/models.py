"""Модели блога: статьи для SEO и удержания пользователя на сайте."""

from django.db import models


class Article(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Адрес страницы", max_length=200, unique=True)
    lead = models.TextField(
        "Лид", blank=True, help_text="Короткий абзац под заголовком и в карточке ленты"
    )
    # текст храним готовым HTML: внутри h2 с id для якорей, блоки note и ссылки ключевыми фразами
    body = models.TextField("Текст статьи (HTML)")
    cover = models.CharField(
        "Обложка (static)",
        max_length=255,
        blank=True,
        help_text="Например: img/news/customs-2026.webp",
    )
    is_published = models.BooleanField("Опублирована", default=True)
    published_at = models.DateTimeField("Опубликована", auto_now_add=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
