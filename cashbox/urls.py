from django.urls import path

from . import views

app_name = 'cashbox'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pagamento/novo/', views.payment_create, name='payment_create'),
    path('movimento/novo/', views.movement_create, name='movement_create'),
    path('fechar/<str:date>/', views.daily_closure, name='daily_closure'),
    path('fechamentos/', views.closures, name='closures'),
    path('fechamentos/novo/', views.period_closure_create, name='period_closure_create'),
]
