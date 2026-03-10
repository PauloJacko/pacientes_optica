from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import PacienteForm
from django.shortcuts import render, get_object_or_404
from usuarios.models import Paciente
from evaluaciones.models import Evaluacion


@require_POST
def crear_paciente(request):

    form = PacienteForm(request.POST)

    if form.is_valid():
        paciente = form.save()

        return JsonResponse({
            'success': True,
            'paciente_id': paciente.id,
            'nombre': paciente.nombre
        })

    return JsonResponse({
        'success': False,
        'errors': form.errors
    })


def ficha_paciente(request, paciente_id):

    paciente = get_object_or_404(Paciente, id=paciente_id)

    evaluaciones = Evaluacion.objects.filter(
        paciente=paciente
    ).order_by("-fecha")

    return render(request, "usuarios/ficha_paciente.html", {
        "paciente": paciente,
        "evaluaciones": evaluaciones
    })
