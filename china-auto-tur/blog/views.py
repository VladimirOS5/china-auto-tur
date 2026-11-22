from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import manager_required
from .models import Post
from .forms import PostForm


def post_list_view(request):
    if request.user.is_authenticated and request.user.is_manager:
        posts = Post.objects.select_related('author').all()
    else:
        posts = Post.objects.select_related('author').filter(is_published=True)

    return render(request, 'blog/list.html', {'posts': posts})


def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/article.html', {'post': post})


@manager_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Новость успешно опубликована.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Добавить новость',
    })


@manager_required
def post_edit_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость обновлена.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': f'Редактировать: {post.title}',
    })
    



@manager_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Новость удалена.')
        return redirect('post_list')
    return redirect('post_detail', pk=pk)