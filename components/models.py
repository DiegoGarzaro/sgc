from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from brands.models import Brand
from categories.models import Category
from packages.models import Package
from sub_categories.models import SubCategory
from suppliers.models import Supplier


class Component(models.Model):
    title = models.CharField(max_length=500)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="components"
    )
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.PROTECT, related_name="components"
    )
    package = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="components"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="components"
    )
    description = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    equivalent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equivalents",
    )
    datasheet = models.FileField(upload_to="datasheets/", null=True, blank=True)
    image = models.ImageField(upload_to="component_images/", null=True, blank=True)
    serie_number = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True, default=Decimal("0.00")
    )
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name="component_quantity_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0) | models.Q(price__isnull=True),
                name="component_price_non_negative",
            ),
        ]

    def clean(self) -> None:
        """Validate model-level business rules.

        Raises:
            ValidationError: If quantity is negative or price is negative.
        """
        errors: dict[str, str] = {}
        if self.quantity is not None and self.quantity < 0:
            errors["quantity"] = "Quantidade não pode ser negativa."
        if self.price is not None and self.price < 0:
            errors["price"] = "Preço não pode ser negativo."
        if errors:
            raise ValidationError(errors)

    @property
    def total_value(self) -> Decimal:
        """Calculate the total inventory value for this component.

        Returns:
            Decimal: Product of price and quantity.
        """
        return (self.price or Decimal("0")) * (self.quantity or 0)

    def __str__(self) -> str:
        return self.title

    @property
    def purchase_options_count(self) -> int:
        """Return how many supplier purchase options exist for this component."""
        if not self.pk:
            return 0
        supplier_manager = getattr(self, "suppliers", None)
        if supplier_manager is None:
            return 0
        return supplier_manager.count()

    @property
    def purchase_options_label(self) -> str | None:
        """Return a short label describing available purchase options."""
        options_count = self.purchase_options_count
        if options_count:
            suffix = "opção" if options_count == 1 else "opções"
            return f"{options_count} {suffix} de compra"
        return self.serie_number


class ComponentSupplier(models.Model):
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="suppliers"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    serie_number = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        supplier_name = self.supplier.name if self.supplier_id else "Sem fornecedor"
        serie_number = self.serie_number or "Sem número de série"
        return f"{supplier_name} - {serie_number}"
