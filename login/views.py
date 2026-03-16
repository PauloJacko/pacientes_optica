from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Max
from django.core.paginator import Paginator

from usuarios.models import Paciente
from usuarios.forms import PacienteForm
from evaluaciones.forms import EvaluacionForm
from evaluaciones.models import Evaluacion

from django.utils.timezone import now
from django.db.models import Count

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            auth_login(request, user)
            return redirect('dashboard')

        else:

            return render(request, 'login/login.html', {
                'error': 'Credenciales inválidas'
            })

    return render(request, 'login/login.html')


@login_required
def dashboard(request):

    pacientes_lista = Paciente.objects.all().order_by('-fecha_creacion')

    nombre = request.GET.get('nombre')
    rut = request.GET.get('rut')
    institucion = request.GET.get('institucion')

    if nombre:
        pacientes_lista = pacientes_lista.filter(nombre__icontains=nombre)

    if rut:
        pacientes_lista = pacientes_lista.filter(rut__icontains=rut)

    if institucion:
        pacientes_lista = pacientes_lista.filter(institucion__icontains=institucion)

    paginator = Paginator(pacientes_lista, 12)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)

    paciente_form = PacienteForm()
    evaluacion_form = EvaluacionForm()

    # -----------------------------
    # MÉTRICAS PARA DASHBOARD EMPRESA
    # -----------------------------

    mes_actual = now().month
    anio_actual = now().year

    # pacientes creados este mes
    pacientes_mes = Paciente.objects.filter(
        fecha_creacion__month=mes_actual,
        fecha_creacion__year=anio_actual
    ).count()

    # total evaluaciones en el sistema
    evaluaciones_total = Evaluacion.objects.count()

    # instituciones distintas atendidas este mes
    instituciones_mes = Paciente.objects.filter(
        fecha_creacion__month=mes_actual,
        fecha_creacion__year=anio_actual
    ).values('institucion').exclude(institucion__isnull=True).exclude(institucion="").distinct().count()

    # -----------------------------
    # ENVÍO DE DATOS AL TEMPLATE
    # -----------------------------

    return render(request, 'login/dashboard.html', {
        'pacientes': pacientes,
        'paciente_form': paciente_form,
        'evaluacion_form': evaluacion_form,

        # métricas
        'pacientes_mes': pacientes_mes,
        'evaluaciones_total': evaluaciones_total,
        'instituciones_mes': instituciones_mes
    })


def logout_view(request):

    logout(request)
    return redirect('login')

@require_POST
@login_required
def eliminar_paciente(request, id):

    try:
        paciente = Paciente.objects.get(id=id)
        paciente.delete()

        return JsonResponse({'success': True})

    except Paciente.DoesNotExist:

        return JsonResponse({'success': False})

@login_required
def imprimir_recetas(request):

    pacientes = Paciente.objects.all()

    nombre = request.GET.get('nombre')
    rut = request.GET.get('rut')
    institucion = request.GET.get('institucion')

    if nombre:
        pacientes = pacientes.filter(nombre__icontains=nombre)

    if rut:
        pacientes = pacientes.filter(rut__icontains=rut)

    if institucion:
        pacientes = pacientes.filter(institucion__icontains=institucion)

    recetas = []

    for paciente in pacientes:

        evaluacion = Evaluacion.objects.filter(
            paciente=paciente
        ).order_by('-fecha').first()

        if evaluacion:

            recetas.append({
                "paciente": paciente,
                "evaluacion": evaluacion
            })

    return render(request, "evaluaciones/receta.html", {
        "recetas": recetas
    })

@login_required
def dashboard_empresa(request):

    mes_actual = now().month
    anio_actual = now().year

    pacientes_mes = Paciente.objects.filter(
        fecha_creacion__month=mes_actual,
        fecha_creacion__year=anio_actual
    ).count()

    evaluaciones_total = Evaluacion.objects.count()

    instituciones_mes = Paciente.objects.values('institucion').distinct().count()

    return render(request, 'login/dashboard_empresa.html', {
        'pacientes_mes': pacientes_mes,
        'evaluaciones_total': evaluaciones_total,
        'instituciones_mes': instituciones_mes
    })