from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from core.models import User

class Command(createsuperuser.Command):
    def handle(self, *args, **options):
        options['interactive'] = True  # Ensure interactive mode
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        if not username or not email or not password:
            raise CommandError("Username, email, and password are required.")

        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists.")

        if User.objects.filter(email=email).exists():
            raise CommandError(f"Email '{email}' already exists.")

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type='super_admin',  # Set default user_type to super_admin
            is_approved=True
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully with role 'super_admin'."))