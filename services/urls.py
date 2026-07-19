from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('novo/', views.service_create, name='create'),
    path('<int:pk>/editar/', views.service_edit, name='edit'),
    path('<int:pk>/precos/', views.service_prices_update, name='prices_update'),
    path('rapido/', views.service_quick_create, name='quick_create'),
    path('preco/', views.service_price_lookup, name='price_lookup'),
]
