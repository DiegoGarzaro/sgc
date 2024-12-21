import json
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from app import metrics

from .forms import ComponentForm
from .models import Brand, Category, Component, SubCategory


class ComponentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Component
    template_name = "component_list.html"
    context_object_name = "components"
    paginate_by = 10
    permission_required = "components.view_component"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters
        title = self.request.GET.get("title")
        category = self.request.GET.get("category")
        sub_category = self.request.GET.get("sub_category")
        brand = self.request.GET.get("brand")

        # Get sorting parameters
        sort_by = self.request.GET.get("sort", "title")  # Default to title
        direction = self.request.GET.get("order", "asc")

        # Apply filters
        if title:
            queryset = queryset.filter(title__icontains=title)
        if category:
            queryset = queryset.filter(category__id=category)
        if sub_category:
            queryset = queryset.filter(sub_category__id=sub_category)
        if brand:
            queryset = queryset.filter(brand__id=brand)

        # Apply sorting
        if sort_by in ["title", "quantity"]:  # Add valid sort fields here
            if direction == "desc":
                sort_by = f"-{sort_by}"
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component_metrics"] = metrics.get_component_metrics()
        context["categories"] = Category.objects.all()
        context["sub_categories"] = SubCategory.objects.all()
        context["brands"] = Brand.objects.all()

        # Add sorting parameters to context
        context["current_sort"] = self.request.GET.get("sort", "title")
        context["current_order"] = self.request.GET.get("order", "asc")

        return context


class ComponentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Component
    template_name = "component_create.html"
    form_class = ComponentForm
    success_url = reverse_lazy("component_list")
    permission_required = "components.add_component"


class ComponentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Component
    template_name = "component_detail.html"
    context_object_name = "component"
    permission_required = "components.view_component"


class ComponentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Component
    template_name = "component_update.html"
    form_class = ComponentForm
    success_url = reverse_lazy("component_list")
    permission_required = "components.change_component"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        component = self.object  # The component being edited

        # All components excluding the current one
        all_components = Component.objects.exclude(id=component.id)
        context["all_components_json"] = json.dumps(
            list(all_components.values("id", "title", "serie_number")),
            cls=DjangoJSONEncoder,
        )

        # Existing equivalents for preloading
        equivalent_components = component.equivalents.all()
        context["existing_equivalents_json"] = json.dumps(
            list(equivalent_components.values("id", "title", "serie_number")),
            cls=DjangoJSONEncoder,
        )

        # Add current subcategory info
        if component.sub_category:
            context["current_subcategory"] = json.dumps({
                'id': component.sub_category.id,
                'name': component.sub_category.name
            }, cls=DjangoJSONEncoder)

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Process the equivalent components from the POST request
        equivalent_ids = self.request.POST.getlist("equivalent[]")
        equivalents = Component.objects.filter(id__in=equivalent_ids)
        self.object.equivalents.set(equivalents)

        return response


class ComponentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Component
    template_name = "component_delete.html"
    success_url = reverse_lazy("component_list")
    permission_required = "components.delete_component"


def subcategories_api(request):
    category_id = request.GET.get("category_id")
    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id).values("id", "name")
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)
