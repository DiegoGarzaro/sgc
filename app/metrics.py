from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.utils import timezone
from django.utils.formats import number_format

from categories.models import Category
from components.models import Component
from suppliers.models import Supplier


def get_component_metrics() -> dict:
    """Aggregate top-level inventory metrics in a single DB query.

    Returns:
        dict: Keys are total_quantity (int), total_price (str, formatted),
            and component_count (int).
    """
    result = Component.objects.aggregate(
        total_quantity=Sum("quantity"),
        component_count=Count("id"),
        total_price=Sum(
            ExpressionWrapper(
                F("price") * F("quantity"),
                output_field=DecimalField(max_digits=20, decimal_places=2),
            )
        ),
    )

    return {
        "total_quantity": result["total_quantity"] or 0,
        "total_price": number_format(
            result["total_price"] or 0, decimal_pos=2, force_grouping=True
        ),
        "component_count": result["component_count"] or 0,
    }


def get_supplier_metrics() -> dict:
    """Return total number of suppliers.

    Returns:
        dict: Key is supplier_count (int).
    """
    return {"supplier_count": Supplier.objects.count()}


def get_component_quantity() -> dict:
    """Return daily quantity totals for components created in the last 7 days.

    Returns:
        dict: Keys are dates (list[str]) and values (list[int]).
    """
    today = timezone.now().date()
    dates = [str(today - timezone.timedelta(days=i)) for i in range(7, 0, -1)]
    values = [
        Component.objects.filter(created_at__date=date_str).aggregate(
            total=Sum("quantity")
        )["total"]
        or 0
        for date_str in dates
    ]
    return {"dates": dates, "values": values}


def get_component_quantity_per_category() -> dict:
    """Return total component quantity grouped by category.

    Returns:
        dict: Keys are categories (list[str]) and values (list[int]),
            sorted by quantity descending.
    """
    categories = (
        Category.objects.filter(components__isnull=False)
        .annotate(total_qty=Sum("components__quantity"))
        .order_by("-total_qty")
    )
    return {
        "categories": [c.name for c in categories],
        "values": [c.total_qty or 0 for c in categories],
    }


def get_low_stock_components(threshold: int = 10):
    """Return components whose quantity is below the given threshold.

    Args:
        threshold (int): Maximum quantity to be considered low stock.

    Returns:
        QuerySet: Component queryset ordered by quantity ascending.
    """
    try:
        threshold = int(threshold)
    except (ValueError, TypeError):
        threshold = 10

    return (
        Component.objects.filter(quantity__lt=threshold)
        .select_related("brand", "category")
        .order_by("quantity")
    )
