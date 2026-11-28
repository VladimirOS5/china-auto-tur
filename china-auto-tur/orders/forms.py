from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('car', 'customer_name', 'phone', 'comment')
        labels = {
            'car': 'Автомобиль (необязательно — можно оставить пустым для индивидуального подбора)',
            'customer_name': 'Ваше имя',
            'phone': 'Телефон для связи',
            'comment': 'Комментарий или пожелания',
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Например: Алексей'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 000-00-00'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Укажите желаемую комплектацию, цвет или бюджет...'}),
        }