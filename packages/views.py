from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms


class PackageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Package
    template_name = 'package_list.html'
    context_object_name = 'packages'
    paginate_by = 10
    permission_required = 'packages.view_package'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class PackageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Package
    form_class = forms.PackageForm
    template_name = 'package_create.html'
    success_url = reverse_lazy('package_list')
    permission_required = 'packages.add_package'

    def form_valid(self, form):
        return super().form_valid(form)


class PackageDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Package
    template_name = 'package_detail.html'
    permission_required = 'packages.view_package'


class PackageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Package
    template_name = 'package_update.html'
    form_class = forms.PackageForm
    success_url = reverse_lazy('package_list')
    permission_required = 'packages.change_package'


class PackageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Package
    template_name = 'package_delete.html'
    success_url = reverse_lazy('package_list')
    permission_required = 'packages.delete_package'
