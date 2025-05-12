from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = 'Creates a super admin user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Super admin username')
        parser.add_argument('email', type=str, help='Super admin email')
        parser.add_argument('password', type=str, help='Super admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f"User with username {username} already exists."))
            return
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f"User with email {email} already exists."))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f"Super admin {username} created successfully."))