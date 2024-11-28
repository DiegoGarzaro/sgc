from django.db import models
from categories.models import Category  # Import the Category model


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', null=True, blank=True)
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.category.name} - {self.name}"
