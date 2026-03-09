from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from usuarios.models import Paciente
from usuarios.forms import PacienteForm
from evaluaciones.forms import EvaluacionForm


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

    return render(request, 'login/dashboard.html', {
        'pacientes': pacientes,
        'paciente_form': paciente_form,
        'evaluacion_form': evaluacion_form
    })


def logout_view(request):

    logout(request)
    return redirect('login')
