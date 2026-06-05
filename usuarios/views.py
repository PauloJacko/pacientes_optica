from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from usuarios.models import Paciente
from usuarios.forms import PacienteForm
from evaluaciones.models import Evaluacion
from evaluaciones.forms import EvaluacionForm

@require_POST
@login_required
def crear_paciente(request):
    form = PacienteForm(request.POST)
    if form.is_valid():
        paciente = form.save()
        return JsonResponse({
            'success': True,
            'paciente_id': paciente.id,
            'nombre': paciente.nombre
        })
    return JsonResponse({'success': False, 'errors': form.errors})


@login_required
def ficha_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    evaluaciones = Evaluacion.objects.filter(paciente=paciente).order_by("-fecha")
    evaluacion_form = EvaluacionForm()

    return render(request, "usuarios/ficha_paciente.html", {
        "paciente": paciente,
        "evaluaciones": evaluaciones,
        "evaluacion_form": evaluacion_form
    })


@require_POST
@login_required
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = PacienteForm(request.POST, instance=paciente)
    
    if form.is_valid():
        form.save()
    return redirect("ficha_paciente", paciente_id=paciente.id)


@login_required
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
@login_required
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
@login_required
def eliminar_evaluacion(request, evaluacion_id):
    e = get_object_or_404(Evaluacion, id=evaluacion_id)
    e.delete()
    return JsonResponse({"success": True})