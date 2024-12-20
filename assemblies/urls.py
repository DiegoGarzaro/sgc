from django.urls import path

from . import views

urlpatterns = [
    path("assemblies/list/", views.AssemblyListView.as_view(), name="assembly_list"),
    path("assemblies/create/", views.AssemblyCreateView.as_view(), name="assembly_create"),
    path(
        "assemblies/<int:pk>/detail/",
        views.AssemblyDetailView.as_view(),
        name="assembly_detail",
    ),
    path(
        "assemblies/<int:pk>/update/",
        views.AssemblyUpdateView.as_view(),
        name="assembly_update",
    ),
    path(
        "assemblies/<int:pk>/delete/",
        views.AssemblyDeleteView.as_view(),
        name="assembly_delete",
    ),
]
