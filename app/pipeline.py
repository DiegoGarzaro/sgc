from social_core.exceptions import AuthForbidden


def set_user_inactive(backend, user, is_new=False, *args, **kwargs):
    """
    Sets the user as inactive only if the user is newly created.
    """
    if user and is_new:
        user.is_active = False
        user.save()


def check_user_status(backend, user, *args, **kwargs):
    """
    Checks if the user is active. If not, raises AuthForbidden exception.
    """
    if user and not user.is_active:
        raise AuthForbidden(backend)
