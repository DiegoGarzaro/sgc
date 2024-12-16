# packages/forms.py
from django import forms

from . import models


class PackageForm(forms.ModelForm):
    class Meta:
        model = models.Package
        fields = ["name", "description", "image"]  # Adicionado o campo 'image'
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),  # Widget para upload de arquivo
        }
        labels = {
            "name": "Nome",
            "description": "Descrição",
            "image": "Imagem",  # Label para o campo de imagem
        }
