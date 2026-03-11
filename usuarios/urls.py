from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/', views.crear_paciente, name='crear_paciente'),
    path("paciente/<int:paciente_id>/", views.ficha_paciente, name="ficha_paciente"),
    path("paciente/<int:paciente_id>/editar/", views.editar_paciente, name="editar_paciente")
]