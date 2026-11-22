from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    excerpt = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Краткий анонс (для карточки в списке)'
    )
    content = models.TextField(verbose_name='Текст статьи')
    image = models.ImageField(
        upload_to='news/',
        blank=True,
        null=True,
        verbose_name='Обложка'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Автор'
    )
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title