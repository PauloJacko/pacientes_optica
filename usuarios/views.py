from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import PacienteForm


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