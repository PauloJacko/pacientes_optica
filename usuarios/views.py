from django.shortcuts import render, redirect
from .forms import PacienteForm

def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            return redirect('crear_evaluacion', paciente_id=paciente.id)
    else:
        form = PacienteForm()

    return render(request, 'usuarios/crear_paciente.html', {'form': form})