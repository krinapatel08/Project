from django.core.management.base import BaseCommand
from hr_system.models import HRUser

class Command(BaseCommand):
    help = 'Seed an HR user'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if not HRUser.objects.filter(username=username).exists():
            HRUser.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created HR user: {username} (password: {password})'))
        else:
            self.stdout.write(self.style.WARNING(f'HR user {username} already exists'))
