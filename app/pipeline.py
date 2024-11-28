from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from social_core.exceptions import AuthException


User = get_user_model()

def prevent_duplicate_user(backend, uid, user=None, *args, **kwargs):
    """
    Prevent duplicate accounts for the same email.
    """
    email = kwargs.get('details', {}).get('email')

    # Check if the user already exists
    if email and not user:
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            raise AuthException(
                backend,
                "A user with this email already exists. Please contact support if this is unexpected."
            )


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
    Set the user as inactive after creation.
    """
    if user and user.is_active:  # Ensure this only applies to new users
        user.is_active = False
        user.save()


def check_user_status(backend, user, request, *args, **kwargs):
    """
    Check if the user is active. If not, display a message and redirect to login.
    """
    if user and not user.is_active:
        messages.error(request, 'Your account is pending approval by an administrator.')
        return redirect('login')
