from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
from .forms import EvaluacionForm
from usuarios.models import Paciente
from .models import Evaluacion
from django.db import transaction
from usuarios.forms import PacienteForm

@login_required
@require_POST
def crear_atencion_completa(request):
    paciente_form = PacienteForm(request.POST)
    evaluacion_form = EvaluacionForm(request.POST)

    if paciente_form.is_valid() and evaluacion_form.is_valid():
        try:
            with transaction.atomic():
                nuevo_paciente = paciente_form.save()

                nueva_evaluacion = evaluacion_form.save(commit=False)
                nueva_evaluacion.paciente = nuevo_paciente
                nueva_evaluacion.save()

            return JsonResponse({
                'success': True,
                'evaluacion_id': nueva_evaluacion.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': 'Chanfle! Acaba de ocurrir un error, contactate con Paulo para que lo arregle al toque.'
            }, status=500)
    else:
        errores = {**paciente_form.errors, **evaluacion_form.errors}
        return JsonResponse({
            'success': False, 
            'error': 'Formulario inválido', 
            'errors': errores
        }, status=400)

@login_required 
@require_POST
def crear_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = EvaluacionForm(request.POST)

    if form.is_valid():
        evaluacion = form.save(commit=False)
        evaluacion.paciente = paciente
        evaluacion.save()
        return JsonResponse({'success': True})

    return JsonResponse({
        'success': False,
        'error': 'Formulario inválido',
        'errors': form.errors
    }, status=400)

@login_required
def ver_receta(request, evaluacion_id):

    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id)

    recetas = [{
        "paciente": evaluacion.paciente,
        "evaluacion": evaluacion
    }]

    return render(request, "evaluaciones/receta.html", {
        "recetas": recetas
    })