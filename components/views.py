import json
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
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

ALLOWED_FILTER_FIELDS = frozenset(
    {
        "title",
        "serie_number",
        "location",
        "description",
        "quantity",
        "price",
        "category__name",
        "sub_category__name",
        "brand__name",
        "package__name",
    }
)

ALLOWED_FILTER_LOOKUPS = frozenset(
    {
        "icontains",
        "exact",
        "gte",
        "lte",
        "gt",
        "lt",
    }
)

ALLOWED_SORT_FIELDS = frozenset({"title", "quantity", "price"})


class FilterStateMixin:
    """Mixin to handle filter state persistence across CRUD operations."""

    def get_success_url(self) -> str:
        """Return component list URL preserving current filter and sort state.

        Returns:
            str: URL with encoded filter query parameters.
        """
        url = reverse("component_list")

        filter_params: dict[str, list[str] | str] = {}
        filter_fields = self.request.GET.getlist("filterField[]", [])
        filter_lookups = self.request.GET.getlist("filterLookup[]", [])
        filter_values = self.request.GET.getlist("filterValue[]", [])

        if filter_fields:
            filter_params["filterField[]"] = filter_fields
        if filter_lookups:
            filter_params["filterLookup[]"] = filter_lookups
        if filter_values:
            filter_params["filterValue[]"] = filter_values

        sort = self.request.GET.get("sort")
        order = self.request.GET.get("order")
        if sort:
            filter_params["sort"] = sort
        if order:
            filter_params["order"] = order

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
        queryset = (
            super()
            .get_queryset()
            .select_related("category", "sub_category", "brand", "package")
        )
        dynamic_filter = Q()

        fields = self.request.GET.getlist("filterField[]")
        lookups = self.request.GET.getlist("filterLookup[]")
        values = self.request.GET.getlist("filterValue[]")

        for field, lookup, value in zip(fields, lookups, values, strict=False):
            if (
                field
                and lookup
                and value
                and field in ALLOWED_FILTER_FIELDS
                and lookup in ALLOWED_FILTER_LOOKUPS
            ):
                filter_expression = f"{field}__{lookup}"
                dynamic_filter &= Q(**{filter_expression: value})

        queryset = queryset.filter(dynamic_filter)

        sort_by = self.request.GET.get("sort", "title")
        direction = self.request.GET.get("order", "asc")
        if sort_by in ALLOWED_SORT_FIELDS:
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

        context["filter_params"] = urlencode(self.request.GET, doseq=True)

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
        context["filter_params"] = urlencode(self.request.GET, doseq=True)
        return context


@login_required
def load_subcategories(request):
    category_id = request.GET.get("category_id")
    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id).values(
            "id", "name"
        )
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)
