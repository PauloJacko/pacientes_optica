from django.db import models
from usuarios.models import Paciente

class Evaluacion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    
    # LEJOS
    lejos_od_esf = models.CharField(max_length=10, blank=True)
    lejos_od_cil = models.CharField(max_length=10, blank=True)
    lejos_od_eje = models.CharField(max_length=10, blank=True)
    lejos_od_dp = models.CharField(max_length=10, blank=True)

    lejos_oi_esf = models.CharField(max_length=10, blank=True)
    lejos_oi_cil = models.CharField(max_length=10, blank=True)
    lejos_oi_eje = models.CharField(max_length=10, blank=True)
    lejos_oi_dp = models.CharField(max_length=10, blank=True)

    # CERCA
    cerca_od_esf = models.CharField(max_length=10, blank=True)
    cerca_od_cil = models.CharField(max_length=10, blank=True)
    cerca_od_eje = models.CharField(max_length=10, blank=True)
    cerca_od_dp = models.CharField(max_length=10, blank=True)

    cerca_oi_esf = models.CharField(max_length=10, blank=True)
    cerca_oi_cil = models.CharField(max_length=10, blank=True)
    cerca_oi_eje = models.CharField(max_length=10, blank=True)
    cerca_oi_dp = models.CharField(max_length=10, blank=True)

    observaciones = models.TextField(blank=True)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación {self.paciente.nombre} - {self.fecha}"