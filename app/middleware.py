
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthForbidden
from django.shortcuts import redirect
from django.contrib import messages

class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthForbidden):
            messages.error(request, 'Sua conta está pendente de aprovação.')
            return redirect('login')
        return super().process_exception(request, exception)