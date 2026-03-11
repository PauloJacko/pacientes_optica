from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import PacienteForm
from django.shortcuts import render, get_object_or_404, redirect
from usuarios.models import Paciente
from evaluaciones.models import Evaluacion
from .models import Paciente
from evaluaciones.forms import EvaluacionForm

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

    evaluacion_form = EvaluacionForm()

    return render(request, "usuarios/ficha_paciente.html", {
        "paciente": paciente,
        "evaluaciones": evaluaciones,
        "evaluacion_form": evaluacion_form
    })

def editar_paciente(request, paciente_id):

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":

        paciente.nombre = request.POST.get("nombre")
        paciente.rut = request.POST.get("rut")
        paciente.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        paciente.telefono = request.POST.get("telefono")
        paciente.institucion = request.POST.get("institucion")
        paciente.anamnesis = request.POST.get("anamnesis")

        paciente.save()

    return redirect("ficha_paciente", paciente_id=paciente.id)