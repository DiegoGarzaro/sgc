import json
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
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


class FilterStateMixin:
    """Mixin to handle filter state persistence"""

    def get_success_url(self):
        # Get the base success URL
        url = reverse("component_list")

        # Get all filter parameters from the request
        filter_params = {}
        filter_fields = self.request.GET.getlist("filterField[]", [])
        filter_lookups = self.request.GET.getlist("filterLookup[]", [])
        filter_values = self.request.GET.getlist("filterValue[]", [])

        # Add them to the parameters if they exist
        if filter_fields:
            filter_params["filterField[]"] = filter_fields
        if filter_lookups:
            filter_params["filterLookup[]"] = filter_lookups
        if filter_values:
            filter_params["filterValue[]"] = filter_values

        # Add sorting parameters if they exist
        sort = self.request.GET.get("sort")
        order = self.request.GET.get("order")
        if sort:
            filter_params["sort"] = sort
        if order:
            filter_params["order"] = order

        # If we have any parameters, add them to the URL
        if filter_params:
            return f"{url}?{urlencode(filter_params, doseq=True)}"
        return url


class ComponentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Component
    template_name = "component_list.html"
    context_object_name = "components"
    paginate_by = 10
    permission_required = "components.view_component"

    def get_queryset(self):
        queryset = super().get_queryset()
        dynamic_filter = Q()

        fields = self.request.GET.getlist("filterField[]")
        lookups = self.request.GET.getlist("filterLookup[]")
        values = self.request.GET.getlist("filterValue[]")

        for field, lookup, value in zip(fields, lookups, values):
            if field and lookup and value:
                filter_expression = f"{field}__{lookup}"
                dynamic_filter &= Q(**{filter_expression: value})

        queryset = queryset.filter(dynamic_filter)

        sort_by = self.request.GET.get("sort", "title")
        direction = self.request.GET.get("order", "asc")
        if sort_by in ["title", "quantity"]:
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
        context["current_sort"] = self.request.GET.get("sort", "title")
        context["current_order"] = self.request.GET.get("order", "asc")

        # Add filter state to context
        context["filter_state"] = {
            "fields": self.request.GET.getlist("filterField[]"),
            "lookups": self.request.GET.getlist("filterLookup[]"),
            "values": self.request.GET.getlist("filterValue[]"),
        }
        return context


class ComponentCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, FilterStateMixin, CreateView
):
    model = Component
    template_name = "component_create.html"
    form_class = ComponentForm
    permission_required = "components.add_component"


class ComponentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Component
    template_name = "component_detail.html"
    context_object_name = "component"
    permission_required = "components.view_component"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter parameters to context for back button
        context["filter_params"] = urlencode(self.request.GET, doseq=True)
        return context


class ComponentUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, FilterStateMixin, UpdateView
):
    model = Component
    template_name = "component_update.html"
    form_class = ComponentForm
    permission_required = "components.change_component"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        component = self.object

        # Add filter parameters to context
        context["filter_params"] = urlencode(self.request.GET, doseq=True)

        # Existing context data
        all_components = Component.objects.exclude(id=component.id)
        context["all_components_json"] = json.dumps(
            list(all_components.values("id", "title", "serie_number")),
            cls=DjangoJSONEncoder,
        )

        equivalent_components = component.equivalents.all()
        context["existing_equivalents_json"] = json.dumps(
            list(equivalent_components.values("id", "title", "serie_number")),
            cls=DjangoJSONEncoder,
        )

        if component.sub_category:
            context["current_subcategory"] = json.dumps(
                {"id": component.sub_category.id, "name": component.sub_category.name},
                cls=DjangoJSONEncoder,
            )

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        equivalent_ids = self.request.POST.getlist("equivalent[]")
        equivalents = Component.objects.filter(id__in=equivalent_ids)
        self.object.equivalents.set(equivalents)
        return response


class ComponentDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, FilterStateMixin, DeleteView
):
    model = Component
    template_name = "component_delete.html"
    permission_required = "components.delete_component"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter parameters to context for cancel button
        context["filter_params"] = urlencode(self.request.GET, doseq=True)
        return context


def load_subcategories(request):
    category_id = request.GET.get("category_id")
    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id).values(
            "id", "name"
        )
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)
