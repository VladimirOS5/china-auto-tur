import re

from django.shortcuts import render, get_object_or_404

from .models import Article


def news(request):
    return render(request, "news.html", {"articles": Article.objects.all()})


def article(request, slug):
    a = get_object_or_404(Article, slug=slug)
    # оглавление из заголовков h2 с id: якоря в начале статьи
    anchors = re.findall(r"<h2 id=\"([^\"]+)\">([^<]+)</h2>", a.body)
    others = Article.objects.exclude(pk=a.pk)[:3]
    return render(request, "article.html", {"a": a, "anchors": anchors, "others": others})
