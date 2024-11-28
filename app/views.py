import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect
from . import metrics

@login_required(login_url='login')
def home(request):
    # Lista padrão de thresholds
    standard_thresholds = [5, 10, 15, 20, 25, 50]
    
    # Obtém o threshold a partir do parâmetro GET, padrão é 10 se não for fornecido
    low_stock_threshold = request.GET.get('low_stock_threshold', 10)
    
    # Converte low_stock_threshold para inteiro
    try:
        low_stock_threshold = int(low_stock_threshold)
    except ValueError:
        low_stock_threshold = 10  # Valor padrão se a conversão falhar

    component_metrics = metrics.get_component_metrics()
    component_quantity = metrics.get_component_quantity()
    component_quantity_per_category = metrics.get_component_quantity_per_category()
    
    # Obtém os componentes com estoque baixo com o threshold especificado
    low_stock_components = metrics.get_low_stock_components(threshold=low_stock_threshold)

    context = {
        'component_metrics': component_metrics,
        'component_quantity': json.dumps(component_quantity),
        'component_quantity_per_category': json.dumps(component_quantity_per_category),
        'low_stock_components': low_stock_components,
        'low_stock_threshold': low_stock_threshold,  # Garante que é um inteiro no template
        'standard_thresholds': standard_thresholds,  # Passa a lista para o template
    }
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