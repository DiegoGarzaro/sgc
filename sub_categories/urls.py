from django.urls import path
from . import views


urlpatterns = [
    path('sub_categories/list/', views.SubCategoryListView.as_view(), name='sub_category_list'),
    path('sub_categories/create/', views.SubCategoryCreateView.as_view(), name='sub_category_create'),
    path('sub_categories/<int:pk>/detail/', views.SubCategoryDetailView.as_view(), name='sub_category_detail'),
    path('sub_categories/<int:pk>/update/', views.SubCategoryUpdateView.as_view(), name='sub_category_update'),
    path('sub_categories/<int:pk>/delete/', views.SubCategoryDeleteView.as_view(), name='sub_category_delete'),
]