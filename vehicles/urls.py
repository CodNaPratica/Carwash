from django.urls import path

from . import views

app_name = 'vehicles'

urlpatterns = [
    path('inicio/', views.vehicle_home, name='home'),
    path('', views.vehicle_list, name='list'),
    path('novo/', views.vehicle_create, name='create'),
    path('<int:pk>/editar/', views.vehicle_edit, name='edit'),
    path('<int:pk>/apagar/', views.vehicle_trash, name='trash'),
    path('<int:pk>/adotar/', views.vehicle_adopt, name='adopt'),
    path('lixo/', views.vehicle_trash_list, name='trash_list'),
    path('lixo/<int:pk>/restaurar/', views.vehicle_restore, name='restore'),
    path('lixo/<int:pk>/apagar-definitivo/', views.vehicle_permanent_delete, name='permanent_delete'),
    path('tipos/novo/', views.vehicle_type_create, name='type_create'),
    path('tipos/<int:pk>/aprovar/', views.vehicle_type_approve, name='type_approve'),
    path('tipos/<int:pk>/apagar/', views.vehicle_type_delete, name='type_delete'),
]
