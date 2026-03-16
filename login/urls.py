from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('pacientes/eliminar/<int:id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('recetas/imprimir/', views.imprimir_recetas, name='imprimir_recetas'),
    path('dashboard/empresa/', views.dashboard_empresa, name='dashboard_empresa'),
]