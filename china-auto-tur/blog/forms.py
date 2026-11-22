from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'excerpt', 'content', 'image', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Обзор нового Zeekr 001'}),
            'excerpt': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Короткое описание в 1–2 предложения...'}),
            'content': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Полный текст новости или обзора...'}),
        }