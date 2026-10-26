import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the private account used by the demo deployment."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_DEPLOY_USERNAME")
        password = os.environ.get("DJANGO_DEPLOY_PASSWORD")
        if not username or not password:
            raise CommandError(
                "Set DJANGO_DEPLOY_USERNAME and DJANGO_DEPLOY_PASSWORD "
                "in the deployment environment."
            )

        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username)
        validate_password(password, user=user)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS("Deployment account is ready."))
