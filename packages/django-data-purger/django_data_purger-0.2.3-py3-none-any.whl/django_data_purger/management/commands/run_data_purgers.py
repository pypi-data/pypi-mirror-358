from typing import Any

from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from django_data_purger.services.data_purger import run_data_purgers


class Command(BaseCommand):
    help: str = "Removes stale database objects."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--force", default=False, action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        force = options["force"]

        run_data_purgers(dry_run=not force)
