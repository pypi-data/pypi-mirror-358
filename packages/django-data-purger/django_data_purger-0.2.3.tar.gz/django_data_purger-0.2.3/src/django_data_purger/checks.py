from typing import Any

from django.core.checks import Error, Warning

from .conf import settings
from .enums import DataPurgerAction
from .exceptions import DataPurgerImportException, DataPurgerInvalidConfiguration
from .services import import_data_purger


def check_data_purgers(app_configs: Any, **kwargs: Any) -> list[Warning | Error]:
    errors: list[Warning | Error] = []

    for data_purger_import in settings.DATA_PURGERS:
        # Make sure the data purger can be imported.
        try:
            data_purger_cls = import_data_purger(data_purger_import)
        except DataPurgerImportException:
            errors.append(
                Error(
                    f"django-data-purger is not able to import the data "
                    f"purger {data_purger_import}.",
                    hint=f"Make sure the {data_purger_import} entry in "
                    "settings.DATA_PURGERS can be imported.",
                )
            )
            continue

        # Make sure we are able to retrieve the expected affected models tuples.
        for action in DataPurgerAction:
            try:
                data_purger_cls.expected_affected_models(action=action)
            except DataPurgerInvalidConfiguration:
                errors.append(
                    Error(
                        f"django-data-purger could not find the expected affected "
                        f"models when {action} operations is executed by "
                        f"{data_purger_import}.",
                        hint=f"Make sure the expected_{action.value}_models attr on "
                        f"the data purger {data_purger_import} is a list of strings.",
                    )
                )

    return errors
