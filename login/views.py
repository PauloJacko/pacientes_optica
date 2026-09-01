from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Max, Count, Q, Avg
from django.core.paginator import Paginator


from usuarios.models import Paciente
from usuarios.forms import PacienteForm
from evaluaciones.forms import EvaluacionForm
from evaluaciones.models import Evaluacion

from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
from collections import defaultdict
from datetime import timedelta

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit

@csrf_protect
@require_http_methods(["GET", "POST"])
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def login_view(request):
    if getattr(request, 'limited', False):
        return render(request, 'login/login.html', {
            'error': 'Has superado el límite de intentos. Por seguridad, espera 1 minuto antes de volver a intentar.'
        }, status=429)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                request.session.cycle_key()
                auth_login(request, user)
                request.session.set_expiry(0)
                return redirect('dashboard')
            else:
                return render(request, 'login/login.html', {
                    'error': 'Esta cuenta ha sido desactivada.'
                })
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

    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if nombre:
        pacientes_lista = pacientes_lista.filter(nombre__icontains=nombre)

    if rut:
        pacientes_lista = pacientes_lista.filter(rut__icontains=rut)

    if institucion:
        pacientes_lista = pacientes_lista.filter(institucion__icontains=institucion)

    if fecha_desde:
        pacientes_lista = pacientes_lista.filter(fecha_creacion__date__gte=fecha_desde)
        
    if fecha_hasta:
        pacientes_lista = pacientes_lista.filter(fecha_creacion__date__lte=fecha_hasta)

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

    anio_seleccionado = request.GET.get('anio')
    anio_actual = int(anio_seleccionado) if anio_seleccionado else now().year
    
    # -------------------------
    # MÉTRICAS GENERALES
    # -------------------------
    pacientes_mes = Paciente.objects.filter(
        fecha_creacion__year=now().year,
        fecha_creacion__month=now().month
    ).count()

    evaluaciones_total = Evaluacion.objects.count()
    instituciones_mes = Paciente.objects.filter(
        fecha_creacion__year=now().year,
        fecha_creacion__month=now().month
    ).values('institucion').distinct().count()

    total_pacientes_historicos = Paciente.objects.count()
    tasa_recetas = 0
    if total_pacientes_historicos > 0:
        tasa_recetas = round((evaluaciones_total / total_pacientes_historicos) * 100, 1)

    # -------------------------
    # NUEVO: TOP 5 INSTITUCIONES MÁS GRANDES (Del año seleccionado)
    # -------------------------
    top_instituciones_qs = (
        Paciente.objects.filter(fecha_creacion__year=anio_actual)
        .values('institucion')
        .exclude(institucion__isnull=True)
        .exclude(institucion="")
        .annotate(total_pacientes=Count('id'))
        .order_by('-total_pacientes')[:5]
    )

    total_inst_anio = Paciente.objects.filter(fecha_creacion__year=anio_actual).values('institucion').distinct().count()
    total_pac_anio = Paciente.objects.filter(fecha_creacion__year=anio_actual).count()
    promedio_por_operativo = round(total_pac_anio / total_inst_anio, 1) if total_inst_anio > 0 else 0


    # -------------------------
    # DISTRIBUCIÓN DE PATOLOGÍAS 
    # -------------------------
    evaluaciones_anio = Evaluacion.objects.filter(fecha__year=anio_actual)

    presbicia_count = evaluaciones_anio.exclude(cerca_od_esf="").exclude(cerca_od_esf__isnull=True).count()

    astigmatismo_count = (
        evaluaciones_anio.exclude(lejos_od_cil="")
        .exclude(lejos_od_cil__isnull=True)
        .exclude(lejos_od_cil="0")
        .exclude(lejos_od_cil="0.00")
        .count()
    )

    miopia_hipermetropia_count = (
        evaluaciones_anio.exclude(lejos_od_esf="")
        .exclude(lejos_od_esf__isnull=True)
        .filter(Q(lejos_od_cil="") | Q(lejos_od_cil="0") | Q(lejos_od_cil="0.00"))
        .count()
    )

    patologias_data = {
        "Miopía / Hipermetropía": miopia_hipermetropia_count,
        "Astigmatismo": astigmatismo_count,
        "Presbicia (Lectura)": presbicia_count
    }

    # -------------------------
    # PACIENTES POR MES (Tu código existente corregido por año dinámico)
    # -------------------------
    pacientes_activos = Paciente.objects.filter(fecha_creacion__gte=now() - timedelta(days=30)).count()
    
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
    pacientes_del_anio = Paciente.objects.filter(fecha_creacion__year=anio_actual)
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
            if not p.institucion: continue
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
    pacientes_region_qs = Paciente.objects.values('region').annotate(total=Count('id')).order_by('-total')
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
    inicio_mes_actual = hoy.replace(day=1)
    fin_mes_actual = hoy
    fin_mes_anterior = inicio_mes_actual - timedelta(days=1)
    inicio_mes_anterior = fin_mes_anterior.replace(day=1)

    pacientes_mes_actual = Paciente.objects.filter(fecha_creacion__range=(inicio_mes_actual, fin_mes_actual)).count()
    pacientes_mes_anterior = Paciente.objects.filter(fecha_creacion__range=(inicio_mes_anterior, fin_mes_anterior)).count()

    if pacientes_mes_anterior > 0:
        crecimiento = round(((pacientes_mes_actual - pacientes_mes_anterior) / pacientes_mes_anterior) * 100, 1)
    else:
        crecimiento = 100 if pacientes_mes_actual > 0 else 0

    # Años disponibles para el filtro del frontend
    anios_disponibles = Paciente.objects.dates('fecha_creacion', 'year', order='DESC')
    anios = [a.year for a in anios_disponibles] if anios_disponibles else [now().year]

    return render(request, 'login/dashboard_empresa.html', {
        'pacientes_mes': pacientes_mes,
        'evaluaciones_total': evaluaciones_total,
        'instituciones_mes': instituciones_mes,
        'tasa_recetas': tasa_recetas,
        'promedio_por_operativo': promedio_por_operativo,
        'top_instituciones': top_instituciones_qs,
        'patologias_labels': list(patologias_data.keys()),
        'patologias_valores': list(patologias_data.values()),

        'pacientes_por_mes': pacientes_por_mes,
        'instituciones_por_mes': instituciones_por_mes,
        'detalle_meses': detalle_meses,
        'pacientes_por_region': pacientes_por_region,
        'pacientes_activos': pacientes_activos,
        'pacientes_mes_actual': pacientes_mes_actual,
        'pacientes_mes_anterior': pacientes_mes_anterior,
        'crecimiento': crecimiento,
        'anios': anios,
        'anio_actual': anio_actual,
    })