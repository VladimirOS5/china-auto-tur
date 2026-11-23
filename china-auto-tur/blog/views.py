"""Views блога: лента новостей и страница статьи."""

import re

from django.shortcuts import render, get_object_or_404

from .models import Article


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, "blog/list.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # оглавление собираем из заголовков h2 с id: якоря в начале статьи, как требует конспект
    anchors = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', article.body)

    # время чтения: средний темп 200 слов в минуту, теги из текста выкидываем
    words = len(re.sub(r"<[^>]+>", " ", article.body).split())
    minutes = max(1, round(words / 200))

    # другие статьи внизу: человек дочитал и пошёл дальше, поведенческие факторы
    others = Article.objects.filter(is_published=True).exclude(id=article.id)[:3]

    return render(
        request,
        "blog/article.html",
        {
            "article": article,
            "anchors": anchors,
            "minutes": minutes,
            "others": others,
        },
    )
