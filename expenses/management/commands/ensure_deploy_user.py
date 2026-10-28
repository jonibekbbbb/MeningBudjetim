import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
        try:
            validate_password(password, user=User(username=username))
        except ValidationError as error:
            raise CommandError(
                "DJANGO_DEPLOY_PASSWORD is invalid. Set a strong password that "
                "is not too similar to DJANGO_DEPLOY_USERNAME in Render "
                "environment variables."
            ) from error

        user, _ = User.objects.get_or_create(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS("Deployment account is ready."))
