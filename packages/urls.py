from django.urls import path

from . import views

urlpatterns = [
    path("packages/list/", views.PackageListView.as_view(), name="package_list"),
    path("packages/create/", views.PackageCreateView.as_view(), name="package_create"),
    path(
        "packages/<int:pk>/detail/",
        views.PackageDetailView.as_view(),
        name="package_detail",
    ),
    path(
        "packages/<int:pk>/update/",
        views.PackageUpdateView.as_view(),
        name="package_update",
    ),
    path(
        "packages/<int:pk>/delete/",
        views.PackageDeleteView.as_view(),
        name="package_delete",
    ),
]
