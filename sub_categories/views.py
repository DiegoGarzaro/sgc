from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from . import forms, models


class SubCategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.SubCategory
    template_name = "sub_category_list.html"
    context_object_name = "sub_categories"
    paginate_by = 10
    permission_required = "sub_categories.view_subcategory"

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class SubCategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.SubCategory
    form_class = forms.SubCategoryForm  # Specify the form class here
    template_name = "sub_category_create.html"
    success_url = reverse_lazy("sub_category_list")
    permission_required = "sub_categories.add_subcategory"


class SubCategoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.SubCategory
    template_name = "sub_category_detail.html"
    permission_required = "sub_categories.view_subcategory"


class SubCategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.SubCategory
    template_name = "sub_category_update.html"
    form_class = forms.SubCategoryForm
    success_url = reverse_lazy("sub_category_list")
    permission_required = "sub_categories.change_subcategory"


class SubCategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.SubCategory
    template_name = "sub_category_delete.html"
    success_url = reverse_lazy("sub_category_list")
    permission_required = "sub_categories.delete_subcategory"
