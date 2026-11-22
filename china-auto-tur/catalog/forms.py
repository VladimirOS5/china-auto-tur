from decimal import Decimal, InvalidOperation
from pathlib import Path
from django import forms
from django.conf import settings
from django.utils.text import slugify
from .models import Brand, Car


def get_static_car_images():
    choices = [('', '--- Выберите фото из static/img/cars ---')]
    cars_dir = Path(settings.BASE_DIR) / 'static' / 'img' / 'cars'
    allowed_ext = {'.jpg', '.jpeg', '.png', '.webp'}

    if cars_dir.exists():
        for file_path in sorted(cars_dir.rglob('*')):
            if file_path.is_file() and file_path.suffix.lower() in allowed_ext:
                rel_static_path = file_path.relative_to(Path(settings.BASE_DIR) / 'static').as_posix()
                label = file_path.relative_to(cars_dir).as_posix()
                choices.append((rel_static_path, label))

    return choices


class CarForm(forms.ModelForm):
    price = forms.CharField(
        label='Цена (₽)',
        widget=forms.TextInput(attrs={'placeholder': 'Например: 3 500 000'})
    )
    new_brand = forms.CharField(
        required=False,
        label='Или введите новую марку (если нет в списке)',
        widget=forms.TextInput(attrs={'placeholder': 'Например: Omoda'})
    )
    static_image = forms.ChoiceField(
        choices=get_static_car_images,
        required=False,
        label='Фото из папки static/img/cars'
    )

    class Meta:
        model = Car
        fields = (
            'brand',
            'new_brand',
            'model_name',
            'year',
            'price',
            'engine_volume',
            'horsepower',
            'transmission',
            'drive_type',
            'static_image',
            'image',
            'description',
            'is_available',
        )
        labels = {
            'image': 'Или загрузить новое фото с компьютера',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].required = False
        # При редактировании авто сразу подставляем цену с пробелами
        if self.instance and self.instance.pk and self.instance.price is not None:
            self.initial['price'] = f'{int(self.instance.price):,}'.replace(',', ' ')

    def clean_price(self):
        raw_price = self.cleaned_data.get('price', '')
        # Убираем обычные и неразрывные пробелы
        cleaned = str(raw_price).replace(' ', '').replace('\xa0', '').strip()
        try:
            value = Decimal(cleaned)
            if value < 0:
                raise forms.ValidationError('Цена не может быть отрицательной.')
            return value
        except InvalidOperation:
            raise forms.ValidationError('Введите корректное число (можно с пробелами).')

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        new_brand_name = cleaned_data.get('new_brand', '').strip()

        if not brand and not new_brand_name:
            raise forms.ValidationError('Выберите марку из списка или введите название новой.')

        if new_brand_name:
            brand_obj, _ = Brand.objects.get_or_create(
                name__iexact=new_brand_name,
                defaults={'name': new_brand_name, 'slug': slugify(new_brand_name)}
            )
            cleaned_data['brand'] = brand_obj

        return cleaned_data