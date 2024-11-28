from django import forms
from .models import Component

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = [
            'title', 'category', 'sub_category', 'package', 'brand', 
            'description', 'location', 'equivalent', 'datasheet', 
            'image', 'serie_number', 'price', 'quantity'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'sub_category': forms.Select(attrs={'class': 'form-control'}),
            'package': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'equivalent': forms.Select(attrs={'class': 'form-control'}),
            'datasheet': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'serie_number': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Título',
            'category': 'Categoria',
            'sub_category': 'Subcategoria',
            'package': 'Encapsulamento',
            'brand': 'Marca',
            'description': 'Descrição',
            'location': 'Localização',
            'equivalent': 'Equivalente',
            'datasheet': 'Ficha Técnica',
            'image': 'Imagem',
            'serie_number': 'Número de Série',
            'price': 'Preço (BRL)',
            'quantity': 'Quantidade',
        }
