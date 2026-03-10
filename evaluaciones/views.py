from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
from .forms import EvaluacionForm
from usuarios.models import Paciente
from .models import Evaluacion


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

def ver_receta(request, evaluacion_id):

    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)

    return render(request, "evaluaciones/receta.html", {
        "evaluacion": evaluacion,
        "paciente": evaluacion.paciente
    })