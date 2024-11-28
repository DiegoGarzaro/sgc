from django.db.models import Sum, F
from django.utils.formats import number_format
from django.utils import timezone
from components.models import Component
from categories.models import Category
from suppliers.models import Supplier

def get_component_metrics():
    components = Component.objects.all()
    total_quantity = sum((component.quantity or 0) for component in components)
    total_price = sum((component.price or 0) * (component.quantity or 0) for component in components)
    component_count = len(components) or 0

    return dict(
        total_quantity=total_quantity,
        total_price=number_format(total_price, decimal_pos=2, force_grouping=True),
        component_count=component_count
    )

def get_supplier_metrics():
    suppliers = Supplier.objects.all()
    supplier_count = len(suppliers) or 0

    return dict(
        supplier_count=supplier_count
    )

def get_component_quantity():
    today = timezone.now().date()

    dates = [str(today - timezone.timedelta(days=i)) for i in range(7, 0, -1)]
    values = list()

    for date in dates:
        date_components = Component.objects.filter(
            created_at__date=date
        )
        total_quantity = sum(component.quantity or 0 for component in date_components)
        values.append(total_quantity)

    return dict(
        dates=dates,
        values=values,
    )

def get_component_quantity_per_category():
    components = Component.objects.all()
    categories = Category.objects.all()

    quantity_per_category = {}

    for component in components:
        category_id = component.category_id

        if category_id not in quantity_per_category:
            quantity_per_category[category_id] = 0
        
        quantity_per_category[category_id] += component.quantity or 0
        
    category_names = [category.name for category in categories if category.id in quantity_per_category]
    values = [quantity_per_category[category.id] for category in categories if category.id in quantity_per_category]

    return dict(
        categories=category_names,
        values=values
    )

def get_low_stock_components(threshold=10):
    try:
        threshold = int(threshold)
    except (ValueError, TypeError):
        threshold = 10  # Default to 10 if invalid input
    
    low_stock_components = Component.objects.filter(quantity__lt=threshold).order_by('quantity')
    
    return low_stock_components