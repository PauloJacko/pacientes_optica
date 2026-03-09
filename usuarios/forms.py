from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre',
            'rut',
            'fecha_nacimiento',
            'telefono',
            'institucion',
            'anamnesis'
        ]

        widgets = {
            'anamnesis': forms.Textarea(attrs={'rows': 4}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'rut': forms.TextInput(attrs={
                'id': 'rut_input',
                'placeholder': '12.345.678-9',
                'maxlength': '12'
            }),
        }