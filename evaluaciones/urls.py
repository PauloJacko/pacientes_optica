from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/<int:paciente_id>/', views.crear_evaluacion, name='crear_evaluacion'),
    path("receta/<int:evaluacion_id>/", views.ver_receta, name="ver_receta"),
]