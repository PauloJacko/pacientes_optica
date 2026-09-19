import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea un superusuario inicial usando variables de entorno'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Lee credenciales desde el entorno del servidor
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@optica.cl')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('No se definió DJANGO_SUPERUSER_PASSWORD en Render. Omitiendo creación.'))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado con éxito.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'El superusuario "{username}" ya existe.'))