from django.urls import path

from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='list'),
    path('novo/', views.vehicle_create, name='create'),
    path('<int:pk>/editar/', views.vehicle_edit, name='edit'),
    path('<int:pk>/apagar/', views.vehicle_trash, name='trash'),
    path('<int:pk>/adotar/', views.vehicle_adopt, name='adopt'),
    path('lixo/', views.vehicle_trash_list, name='trash_list'),
]
