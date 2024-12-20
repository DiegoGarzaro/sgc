from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication URLs
    path("accounts/", include("django.contrib.auth.urls")),
    # Rotas de redefinição de senha
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            success_url="done/",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Social Authentication
    path("oauth/", include("social_django.urls", namespace="social")),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    # Home page
    path("", views.home, name="home"),
    path("", include("assemblies.urls")),
    path("", include("brands.urls")),
    path("", include("categories.urls")),
    path("", include("sub_categories.urls")),
    path("", include("packages.urls")),
    path("", include("suppliers.urls")),
    path("", include("components.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
