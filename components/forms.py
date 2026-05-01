import os

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from suppliers.models import Supplier

from .models import Component, ComponentSupplier

ALLOWED_DATASHEET_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}


def validate_datasheet_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_DATASHEET_EXTENSIONS:
        raise ValidationError(
            f"Tipo de arquivo não permitido. Use: {', '.join(sorted(ALLOWED_DATASHEET_EXTENSIONS))}"
        )


class ComponentForm(forms.ModelForm):
    datasheet = forms.FileField(
        required=False,
        validators=[validate_datasheet_extension],
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".pdf,.doc,.docx,.xls,.xlsx"}
        ),
        label="Ficha Técnica",
    )

    class Meta:
        model = Component
        fields = [
            "title",
            "category",
            "sub_category",
            "package",
            "brand",
            "description",
            "location",
            "equivalent",
            "datasheet",
            "image",
            "price",
            "quantity",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "sub_category": forms.Select(attrs={"class": "form-control"}),
            "package": forms.Select(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "equivalent": forms.Select(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Título",
            "category": "Categoria",
            "sub_category": "Subcategoria",
            "package": "Encapsulamento",
            "brand": "Marca",
            "description": "Descrição",
            "location": "Localização",
            "equivalent": "Equivalente",
            "image": "Imagem",
            "price": "Preço (BRL)",
            "quantity": "Quantidade",
        }


class ComponentSupplierForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-select bg-secondary bg-opacity-10 border-0 text-white p-3"
            }
        ),
        label="Fornecedor",
        empty_label="Selecione um fornecedor",
    )
    serie_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control bg-secondary bg-opacity-10 border-0 text-white p-3",
                "placeholder": "Ex: 1N4148",
            }
        ),
        label="Número de Série",
    )

    class Meta:
        model = ComponentSupplier
        fields = ["supplier", "serie_number"]


class BaseComponentSupplierFormSet(BaseInlineFormSet):
    default_error_messages = {
        **BaseInlineFormSet.default_error_messages,
        "too_few_forms": "Adicione pelo menos uma opção de compra.",
    }

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        active_forms = []

        for form in self.forms:
            cleaned_data = getattr(form, "cleaned_data", None)
            if not cleaned_data or cleaned_data.get("DELETE"):
                continue

            supplier = cleaned_data.get("supplier")
            serie_number = (cleaned_data.get("serie_number") or "").strip()
            has_existing_instance = bool(form.instance.pk)

            if not supplier and not serie_number and not has_existing_instance:
                continue

            if not supplier:
                form.add_error("supplier", "Selecione um fornecedor.")
                continue

            active_forms.append(form)

        if not active_forms:
            raise ValidationError("Adicione pelo menos uma opção de compra.")


ComponentSupplierFormSet = inlineformset_factory(
    Component,
    ComponentSupplier,
    form=ComponentSupplierForm,
    formset=BaseComponentSupplierFormSet,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
