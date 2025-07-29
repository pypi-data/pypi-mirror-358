from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from django_data_purger.enums import DataPurgerAction
from django_data_purger.exceptions import DataPurgerException
from django_data_purger.services import get_tables_with_data_purging_enabled


class Command(BaseCommand):
    help = "Print tables with data purging enabled."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--action", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        action_value = options["action"]

        try:
            action = DataPurgerAction(action_value)
        except ValueError as exc:
            supported_actions = ", ".join(DataPurgerAction)
            raise DataPurgerException(
                f"Action {action_value} is not a valid action, use one "
                f"of {supported_actions}."
            ) from exc

        tables = get_tables_with_data_purging_enabled(action=action)

        print("Print tables with data purging enabled:")

        for table in tables:
            print(f"- {table}")
