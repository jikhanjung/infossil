from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # author urls
    path('author_list/', views.author_list, name='author_list'),
    path('author_detail/<int:pk>/', views.author_detail, name='author_detail'),
    path('author_add/', views.author_add, name='author_add'),
    path('author_edit/<int:pk>/', views.author_edit, name='author_edit'),
    path('author_delete/<int:pk>/', views.author_delete, name='author_delete'),

    # scientific name urls
    path('taxon_list/', views.taxon_list, name='taxon_list'),
    path('taxon_detail/<int:pk>/', views.taxon_detail, name='taxon_detail'),
    path('taxon_add/', views.taxon_add, name='taxon_add'),
    path('taxon_edit/<int:pk>/', views.taxon_edit, name='taxon_edit'),
    path('taxon_delete/<int:pk>/', views.taxon_delete, name='taxon_delete'),

]