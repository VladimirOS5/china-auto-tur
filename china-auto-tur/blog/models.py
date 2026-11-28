from django.db import models


class Article(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    lead = models.TextField("Лид", blank=True)
    body = models.TextField("Текст HTML")
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title
