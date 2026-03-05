from django.shortcuts import render, get_object_or_404, redirect
from .forms import EvaluacionForm
from usuarios.models import Paciente

def crear_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            evaluacion = form.save(commit=False)
            evaluacion.paciente = paciente
            evaluacion.save()
            return redirect('dashboard')
    else:
        form = EvaluacionForm()

    return render(request, 'evaluaciones/crear_evaluacion.html', {
        'form': form,
        'paciente': paciente
    })