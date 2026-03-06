from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .forms import EvaluacionForm
from usuarios.models import Paciente


@require_POST
def crear_evaluacion(request, paciente_id):

    paciente = get_object_or_404(Paciente, id=paciente_id)

    form = EvaluacionForm(request.POST)

    if form.is_valid():

        evaluacion = form.save(commit=False)
        evaluacion.paciente = paciente
        evaluacion.save()

        return JsonResponse({
            'success': True
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors
    })