from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('evaluaciones/', include('evaluaciones.urls')),
]