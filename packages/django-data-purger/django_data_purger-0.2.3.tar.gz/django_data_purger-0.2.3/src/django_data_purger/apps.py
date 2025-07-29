from django.apps import AppConfig
from django.core import checks

from .checks import check_data_purgers


class DjangoDataPurgerConfig(AppConfig):
    name = "django_data_purger"
    verbose_name = "Django Data Purger"

    def ready(self) -> None:
        checks.register(check_data_purgers)
