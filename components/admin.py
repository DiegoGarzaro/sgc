from django.contrib import admin

from .models import Component, ComponentSupplier


class ComponentSupplierInline(admin.TabularInline):
    model = ComponentSupplier
    extra = 0
    fields = ("supplier", "serie_number")


class ComponentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "sub_category", "brand", "package", "quantity")
    list_filter = ("category", "sub_category", "brand", "package")
    search_fields = ("title", "serie_number", "description", "location")
    inlines = [ComponentSupplierInline]


admin.site.register(Component, ComponentAdmin)
