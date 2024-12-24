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


class AssemblyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Assembly
    template_name = "assembly_list.html"
    context_object_name = "assemblies"
    paginate_by = 10
    permission_required = "assemblies.view_assembly"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters
        name = self.request.GET.get("name")

        # Get sorting parameters
        sort_by = self.request.GET.get("sort", "name")  # Default to title
        direction = self.request.GET.get("order", "asc")

        # Apply filters
        if name:
            queryset = queryset.filter(title__icontains=name)

        # Apply sorting
        if sort_by in ["name"]:  # Add valid sort fields here
            if direction == "desc":
                sort_by = f"-{sort_by}"
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add sorting parameters to context
        context["current_sort"] = self.request.GET.get("sort", "name")
        context["current_order"] = self.request.GET.get("order", "asc")

        return context


class AssemblyCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Assembly
    template_name = "assembly_create.html"
    form_class = forms.AssemblyForm
    success_url = reverse_lazy("assembly_list")
    permission_required = "assemblies.add_assembly"


class AssemblyDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Assembly
    template_name = "assembly_detail.html"
    permission_required = "assemblies.view_assembly"


class AssemblyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Assembly
    template_name = "assembly_update.html"
    form_class = forms.AssemblyForm
    success_url = reverse_lazy("assembly_list")
    permission_required = "assemblies.change_assembly"


class AssemblyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Assembly
    template_name = "assembly_delete.html"
    success_url = reverse_lazy("assembly_list")
    permission_required = "assemblies.delete_assembly"
