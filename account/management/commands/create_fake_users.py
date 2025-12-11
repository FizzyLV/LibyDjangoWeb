from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

try:
    from rest_framework.authtoken.models import Token
except Exception:
    Token = None


class Command(BaseCommand):
    help = "Create fake test users and (optionally) tokens for testing"

    def handle(self, *args, **options):
        User = get_user_model()

        users = [
            {"email": "alice@example.com", "password": "password123", "username": "alice"},
            {"email": "bob@example.com", "password": "secret123", "username": "bob"},
            {"email": "carol@example.com", "password": "passw0rd", "username": "carol"},
        ]

        for u in users:
            user, created = User.objects.get_or_create(email=u["email"], defaults={"username": u["username"]})
            if created:
                user.set_password(u["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {u['email']}"))
            else:
                # Update password to the known test password so login works predictably
                user.set_password(u["password"])
                user.save()
                self.stdout.write(self.style.WARNING(f"User {u['email']} already existed — password updated"))

            if Token is not None:
                token, _ = Token.objects.get_or_create(user=user)
                self.stdout.write(f"Token for {u['email']}: {token.key}")
            else:
                self.stdout.write("rest_framework.authtoken not available — run migrations after installing DRF")

        self.stdout.write(self.style.SUCCESS("Done."))
