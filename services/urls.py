from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('novo/', views.service_create, name='create'),
    path('<int:pk>/editar/', views.service_edit, name='edit'),
    path('rapido/', views.service_quick_create, name='quick_create'),
]
