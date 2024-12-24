# packages/forms.py
from django import forms

from . import models


class PackageForm(forms.ModelForm):
    class Meta:
        model = models.Package
        fields = [
            "name",
            "assembly",
            "description",
            "image",
        ]  # Added the 'assembly' field
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "assembly": forms.Select(
                attrs={"class": "form-control"}
            ),  # Dropdown for assemblies
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),  # Widget for image upload
        }
        labels = {
            "name": "Nome",
            "assembly": "Montagem",  # Label for the 'assembly' field
            "description": "Descrição",
            "image": "Imagem",  # Label for the image field
        }
