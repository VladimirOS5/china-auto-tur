from pathlib import Path
from django import forms
from django.conf import settings
from .models import Car


def get_static_car_images():
    choices = [('', '--- Выберите фото из static/img/cars ---')]
    cars_dir = Path(settings.BASE_DIR) / 'static' / 'img' / 'cars'
    allowed_ext = {'.jpg', '.jpeg', '.png', '.webp'}

    if cars_dir.exists():
        for file_path in sorted(cars_dir.rglob('*')):
            if file_path.is_file() and file_path.suffix.lower() in allowed_ext:
                # Относительный путь для тега static: 'img/cars/geely/1.jpg'
                rel_static_path = file_path.relative_to(Path(settings.BASE_DIR) / 'static').as_posix()
                # Короткая подпись для списка: 'geely/1.jpg'
                label = file_path.relative_to(cars_dir).as_posix()
                choices.append((rel_static_path, label))

    return choices


class CarForm(forms.ModelForm):
    static_image = forms.ChoiceField(
        choices=get_static_car_images,  # передаём саму функцию без скобок ()
        required=False,
        label='Фото из папки static/img/cars'
    )

    class Meta:
        model = Car
        fields = (
            'brand',
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