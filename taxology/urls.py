from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # scientific name urls
    path('taxon_list/', views.taxon_list, name='taxon_list'),
    path('taxon_add/', views.taxon_add, name='taxon_add'),
    path('taxon_edit/<int:pk>/', views.taxon_edit, name='taxon_edit'),
    path('taxon_delete/<int:pk>/', views.taxon_delete, name='taxon_delete'),
    path('taxon_detail/<int:pk>/', views.taxon_detail, name='taxon_detail'),

]