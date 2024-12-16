from django.db import models

from brands.models import Brand
from categories.models import Category
from packages.models import Package
from sub_categories.models import SubCategory


class Component(models.Model):
    # user_group = models.ForeignKey(user_group)
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
        limit_choices_to=models.Q(id__isnull=False),
    )
    datasheet = models.FileField(upload_to="datasheets/", null=True, blank=True)
    image = models.ImageField(
        upload_to="component_images/", null=True, blank=True
    )  # New optional image field
    serie_number = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True, default=0
    )
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title
