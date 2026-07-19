from django.urls import path

from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.reconciliation_view, name='reconciliation'),
    path('caso/<int:pk>/atualizar/', views.update_investigation, name='update_investigation'),
    path('ligar/', views.manual_link, name='manual_link'),
]
