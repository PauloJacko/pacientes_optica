from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/<int:paciente_id>/', views.crear_evaluacion, name='crear_evaluacion'),
]