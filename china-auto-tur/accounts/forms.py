from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Электронная почта'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заменяем или полностью очищаем системные подсказки (help_text)
        self.fields['username'].help_text = '' 
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''  
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone': 'Телефон',
        }


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )