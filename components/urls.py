from django.urls import path
from . import views


urlpatterns = [
    path('components/list/', views.ComponentListView.as_view(), name='component_list'),
    path('components/create/', views.ComponentCreateView.as_view(), name='component_create'),
    path('components/<int:pk>/detail/', views.ComponentDetailView.as_view(), name='component_detail'),
    path('components/<int:pk>/update/', views.ComponentUpdateView.as_view(), name='component_update'),
    path('components/<int:pk>/delete/', views.ComponentDeleteView.as_view(), name='component_delete'),
]