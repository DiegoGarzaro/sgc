from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from social_core.exceptions import AuthException


User = get_user_model()

def prevent_duplicate_user(backend, uid, user=None, *args, **kwargs):
    """
    Prevent duplicate accounts for the same email and associate existing users.
    """
    email = kwargs.get('details', {}).get('email')

    # If no user is associated and email exists, try to find an existing user
    if email and not user:
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            # Associate the existing user with the social account
            return {'user': existing_user}

    # If no email or no user found, allow the pipeline to create a new user
    return {}


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


def set_user_inactive(backend, user, *args, **kwargs):
    """
    Set newly created users as inactive.
    """
    if user and not user.is_active:  # Apply only to new users
        user.is_active = False
        user.save()


def check_user_status(backend, user, request, *args, **kwargs):
    """
    Check if the user is active. If not, display a message and redirect to login.
    """
    if user and not user.is_active:
        messages.error(request, 'Your account is pending approval by an administrator.')
        return redirect('login')
