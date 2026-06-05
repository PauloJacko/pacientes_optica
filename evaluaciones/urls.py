from django.urls import path
from . import views
from usuarios import views as usuarios_views 

urlpatterns = [
    path('nuevo/<int:paciente_id>/', views.crear_evaluacion, name='crear_evaluacion'),
    path("receta/<int:evaluacion_id>/", views.ver_receta, name="ver_receta"),
    path('<int:evaluacion_id>/json/', usuarios_views.evaluacion_json, name='evaluacion_json'),
    path('<int:evaluacion_id>/editar/', usuarios_views.editar_evaluacion, name='editar_evaluacion'),
    path('<int:evaluacion_id>/eliminar/', usuarios_views.eliminar_evaluacion, name='eliminar_evaluacion'),
    path('crear-completo/', views.crear_atencion_completa, name='crear_atencion_completa'),
]