from django.contrib import messages
from django.shortcuts import redirect


def remove_permissions(backend, user, *args, **kwargs):
    """
    Remove todas as permissões e grupos do usuário após a criação.
    """
    if user:
        # Remove todas as permissões diretas
        user.user_permissions.clear()
        # Remove o usuário de todos os grupos
        user.groups.clear()
        # Opcionalmente, definir o usuário como inativo
        user.is_active = False
        user.save()

def check_user_status(backend, user, request, *args, **kwargs):
    """
    Check if the user is active. If not, display a message and redirect to login.
    """
    if user and not user.is_active:
        messages.error(request, 'Sua conta está pendente de aprovação.')
        return redirect('login')