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
        paciente.region = request.POST.get("region")
        paciente.anamnesis = request.POST.get("anamnesis")
        
        paciente.save()

    return redirect("ficha_paciente", paciente_id=paciente.id)

def evaluacion_json(request, evaluacion_id):

    e = get_object_or_404(Evaluacion, id=evaluacion_id)

    return JsonResponse({
        "lejos_od_esf": e.lejos_od_esf,
        "lejos_od_cil": e.lejos_od_cil,
        "lejos_od_eje": e.lejos_od_eje,
        "observaciones": e.observaciones or "",
    })

def evaluacion_json(request, evaluacion_id):
    e = get_object_or_404(Evaluacion, id=evaluacion_id)
    return JsonResponse({
        # LEJOS
        "lejos_od_esf": e.lejos_od_esf,
        "lejos_od_cil": e.lejos_od_cil,
        "lejos_od_eje": e.lejos_od_eje,
        "lejos_od_dp": e.lejos_od_dp,
        
        "lejos_oi_esf": e.lejos_oi_esf,
        "lejos_oi_cil": e.lejos_oi_cil,
        "lejos_oi_eje": e.lejos_oi_eje,
        "lejos_oi_dp": e.lejos_oi_dp,
        
        # CERCA
        "cerca_od_esf": e.cerca_od_esf,
        "cerca_od_cil": e.cerca_od_cil,
        "cerca_od_eje": e.cerca_od_eje,
        "cerca_od_dp": e.cerca_od_dp,
        
        "cerca_oi_esf": e.cerca_oi_esf,
        "cerca_oi_cil": e.cerca_oi_cil,
        "cerca_oi_eje": e.cerca_oi_eje,
        "cerca_oi_dp": e.cerca_oi_dp,
        
        "observaciones": e.observaciones or "",
    })

@require_POST
def editar_evaluacion(request, evaluacion_id):
    e = get_object_or_404(Evaluacion, id=evaluacion_id)

    # MAPEO DE CAMPOS DE LEJOS
    e.lejos_od_esf = request.POST.get("lejos_od_esf")
    e.lejos_od_cil = request.POST.get("lejos_od_cil")
    e.lejos_od_eje = request.POST.get("lejos_od_eje")
    e.lejos_od_dp = request.POST.get("lejos_od_dp")

    e.lejos_oi_esf = request.POST.get("lejos_oi_esf")
    e.lejos_oi_cil = request.POST.get("lejos_oi_cil")
    e.lejos_oi_eje = request.POST.get("lejos_oi_eje")
    e.lejos_oi_dp = request.POST.get("lejos_oi_dp")

    # MAPEO DE CAMPOS DE CERCA
    e.cerca_od_esf = request.POST.get("cerca_od_esf")
    e.cerca_od_cil = request.POST.get("cerca_od_cil")
    e.cerca_od_eje = request.POST.get("cerca_od_eje")
    e.cerca_od_dp = request.POST.get("cerca_od_dp")

    e.cerca_oi_esf = request.POST.get("cerca_oi_esf")
    e.cerca_oi_cil = request.POST.get("cerca_oi_cil")
    e.cerca_oi_eje = request.POST.get("cerca_oi_eje")
    e.cerca_oi_dp = request.POST.get("cerca_oi_dp")

    e.observaciones = request.POST.get("observaciones")
    e.save()

    return JsonResponse({"success": True})

@require_POST
def eliminar_evaluacion(request, evaluacion_id):

    e = get_object_or_404(Evaluacion, id=evaluacion_id)

    e.delete()

    return JsonResponse({
        "success": True
    })

