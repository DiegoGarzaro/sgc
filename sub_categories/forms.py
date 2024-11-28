from django import forms
from .models import SubCategory


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'description', 'category']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),  # Dropdown for categories
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'category': 'Category',
            'name': 'Sub-Category Name',
            'description': 'Description',
        }
