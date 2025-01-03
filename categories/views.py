from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from components.models import Component

from . import forms, models


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Category
    template_name = "category_list.html"
    context_object_name = "categories"
    paginate_by = 10
    permission_required = "categories.view_category"

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Category
    template_name = "category_create.html"
    form_class = forms.CategoryForm
    success_url = reverse_lazy("category_list")
    permission_required = "categories.add_category"


class CategoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Category
    template_name = "category_detail.html"
    permission_required = "categories.view_category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch components associated with this category
        context["components"] = Component.objects.filter(category=self.object)
        return context


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Category
    template_name = "category_update.html"
    form_class = forms.CategoryForm
    success_url = reverse_lazy("category_list")
    permission_required = "categories.change_category"


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Category
    template_name = "category_delete.html"
    success_url = reverse_lazy("category_list")
    permission_required = "categories.delete_category"
