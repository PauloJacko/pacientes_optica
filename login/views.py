from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login/login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'login/login.html')


@login_required
def dashboard(request):
    return render(request, 'login/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')