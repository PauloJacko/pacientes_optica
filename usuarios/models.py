from django.db import models

class Paciente(models.Model):

    REGION_CHOICES = [
        ("XV", "XV - Arica y Parinacota"),
        ("I", "I - Tarapacá"),
        ("II", "II - Antofagasta"),
        ("III", "III - Atacama"),
        ("IV", "IV - Coquimbo"),
        ("V", "V - Valparaíso"),
        ("RM", "RM - Metropolitana"),
        ("VI", "VI - O'Higgins"),
        ("VII", "VII - Maule"),
        ("XVI", "XVI - Ñuble"),
        ("VIII", "VIII - Biobío"),
        ("IX", "IX - La Araucanía"),
        ("XIV", "XIV - Los Ríos"),
        ("X", "X - Los Lagos"),
        ("XI", "XI - Aysén"),
        ("XII", "XII - Magallanes"),
    ]

    nombre = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True)
    institucion = models.CharField(max_length=150, blank=True)
    region = models.CharField(
        max_length=5,
        choices=REGION_CHOICES,
        blank=False,
        null=False
    )
    anamnesis = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.rut}"

    @property
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )