import json
from typing import Union
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.template.loader import render_to_string
from . import metrics

@login_required(login_url='login')
def home(request: HttpRequest) -> Union[HttpResponse, JsonResponse]:
    # List of standard thresholds with type hint
    standard_thresholds: list[int] = [5, 10, 15, 20, 25, 50]

    # Get threshold from GET parameter, default to 10
    low_stock_threshold = request.GET.get('low_stock_threshold', 10)

    # Safer conversion with explicit type casting and range validation
    try:
        low_stock_threshold = max(1, min(int(low_stock_threshold), 100))
    except ValueError:
        low_stock_threshold = 10  # Default value if conversion fails

    # Add error handling for metrics functions
    try:
        component_metrics = metrics.get_component_metrics()
        component_quantity = metrics.get_component_quantity()
        component_quantity_per_category = metrics.get_component_quantity_per_category()
        low_stock_components = metrics.get_low_stock_components(threshold=low_stock_threshold)
    except Exception as e:
        # Log the error or handle it appropriately
        messages.error(request, f"Error retrieving metrics: {str(e)}")
        component_metrics = {}
        component_quantity = {}
        component_quantity_per_category = {}
        low_stock_components = []

    context = {
        'component_metrics': component_metrics,
        'component_quantity': json.dumps(component_quantity),
        'component_quantity_per_category': json.dumps(component_quantity_per_category),
        'low_stock_components': low_stock_components,
        'low_stock_threshold': low_stock_threshold,
        'standard_thresholds': standard_thresholds,
    }

    # Check if the request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the partial template for low stock components
        html = render_to_string('components/_low_stock_components.html', context, request=request)
        return JsonResponse({'html': html})

    # If not AJAX, render the full page
    return render(request, 'home.html', context)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """
        Este método é chamado quando o formulário é válido.
        Aqui, verificamos se o usuário está ativo antes de fazer login.
        """
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, 'Sua conta está pendente de aprovação.')
            return redirect('login')
        else:
            return super().form_valid(form)
