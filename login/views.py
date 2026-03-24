from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Max, Count
from django.core.paginator import Paginator

from usuarios.models import Paciente
from usuarios.forms import PacienteForm
from evaluaciones.forms import EvaluacionForm
from evaluaciones.models import Evaluacion

from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
from collections import defaultdict
from datetime import timedelta

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

    anio_actual = now().year

    # -------------------------
    # MÉTRICAS GENERALES
    # -------------------------
    pacientes_mes = Paciente.objects.filter(
        fecha_creacion__year=anio_actual,
        fecha_creacion__month=now().month
    ).count()

    evaluaciones_total = Evaluacion.objects.count()

    instituciones_mes = Paciente.objects.values('institucion').distinct().count()

    # -------------------------
    # PACIENTES POR MES 
    # -------------------------

    pacientes_activos = Paciente.objects.filter(
        fecha_creacion__gte=now() - timedelta(days=30)
        ).count()
    
    pacientes_por_mes_qs = (
        Paciente.objects
        .filter(fecha_creacion__year=anio_actual)
        .annotate(mes=ExtractMonth('fecha_creacion'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    pacientes_por_mes = [0] * 12

    for item in pacientes_por_mes_qs:
        pacientes_por_mes[item['mes'] - 1] = item['total']

    # -------------------------
    # INSTITUCIONES POR MES 
    # -------------------------
    pacientes_del_anio = Paciente.objects.filter(
        fecha_creacion__year=anio_actual
    )

    instituciones_por_mes_dict = defaultdict(set)

    for p in pacientes_del_anio:
        if p.institucion:
            mes = p.fecha_creacion.month
            institucion_normalizada = p.institucion.strip().lower()
            instituciones_por_mes_dict[mes].add(institucion_normalizada)

    instituciones_por_mes = [0] * 12

    for mes, instituciones in instituciones_por_mes_dict.items():
        instituciones_por_mes[mes - 1] = len(instituciones)

    # -------------------------
    # DETALLE PARA MODALES 
    # -------------------------
    detalle_meses = {}

    for mes in range(1, 13):
        pacientes_mes_qs = Paciente.objects.filter(
            fecha_creacion__year=anio_actual,
            fecha_creacion__month=mes
        )

        instituciones_dict = {}

        for p in pacientes_mes_qs:
            if not p.institucion:
                continue

            inst = p.institucion.strip().lower()

            if inst not in instituciones_dict:
                instituciones_dict[inst] = {
                    "nombre": p.institucion.strip(),
                    "pacientes": []
                }

            instituciones_dict[inst]["pacientes"].append({
                "nombre": p.nombre,
                "rut": p.rut
            })

        detalle_meses[mes] = list(instituciones_dict.values())

    # -------------------------
    # PACIENTES POR REGIÓN
    # -------------------------
    pacientes_region_qs = (
        Paciente.objects
        .values('region')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    pacientes_por_region = []

    for r in pacientes_region_qs:
        pacientes_por_region.append({
            "region": dict(Paciente.REGION_CHOICES).get(r['region'], r['region']),
            "total": r['total']
        })
    
    # -------------------------
    # CRECIMIENTO MENSUAL
    # -------------------------

    hoy = now()

    # Mes actual
    inicio_mes_actual = hoy.replace(day=1)
    fin_mes_actual = hoy

    # Mes anterior
    fin_mes_anterior = inicio_mes_actual - timedelta(days=1)
    inicio_mes_anterior = fin_mes_anterior.replace(day=1)

    # Conteos
    pacientes_mes_actual = Paciente.objects.filter(
        fecha_creacion__range=(inicio_mes_actual, fin_mes_actual)
    ).count()

    pacientes_mes_anterior = Paciente.objects.filter(
        fecha_creacion__range=(inicio_mes_anterior, fin_mes_anterior)
    ).count()

    # % crecimiento
    if pacientes_mes_anterior > 0:
        crecimiento = round(
            ((pacientes_mes_actual - pacientes_mes_anterior) / pacientes_mes_anterior) * 100,
            1
        )
    else:
        crecimiento = 100 if pacientes_mes_actual > 0 else 0

    # -------------------------
    # RENDER
    # -------------------------
    return render(request, 'login/dashboard_empresa.html', {
        'pacientes_mes': pacientes_mes,
        'evaluaciones_total': evaluaciones_total,
        'instituciones_mes': instituciones_mes,

        'pacientes_por_mes': pacientes_por_mes,
        'instituciones_por_mes': instituciones_por_mes,
        'detalle_meses': detalle_meses,
        'pacientes_por_region': pacientes_por_region,
        'pacientes_activos': pacientes_activos,
        'pacientes_mes_actual': pacientes_mes_actual,
        'pacientes_mes_anterior': pacientes_mes_anterior,
        'crecimiento': crecimiento,
    })