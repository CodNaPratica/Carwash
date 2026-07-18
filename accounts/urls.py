from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import BootstrapAuthenticationForm

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html', authentication_form=BootstrapAuthenticationForm),
        name='login',
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('painel-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/novo/', views.user_create, name='user_create'),
    path('usuarios/<int:pk>/editar/', views.user_edit, name='user_edit'),
    path('usuarios/<int:pk>/password/', views.user_set_password, name='user_set_password'),
    path('perfil/', views.profile, name='profile'),
]
