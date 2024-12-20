from django.db import models

from assemblies.models import Assembly


class Package(models.Model):
    name = models.CharField(max_length=500)
    assembly = models.ForeignKey(
        Assembly, on_delete=models.PROTECT, related_name="packages", null=True
    )
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="package", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
