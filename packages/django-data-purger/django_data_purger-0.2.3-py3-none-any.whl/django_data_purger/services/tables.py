from logging import getLogger

from django_data_purger.conf import settings
from django_data_purger.enums import DataPurgerAction
from django_data_purger.exceptions import DataPurgerImportException

from .data_purger import import_data_purger

logger = getLogger(__name__)


def get_tables_with_data_purging_enabled(*, action: DataPurgerAction) -> list[str]:
    """Return a list of tables with data purging enabled."""
    data_purgers_imports = settings.DATA_PURGERS

    tables: set[str] = set()

    for data_purger_import in data_purgers_imports:
        try:
            data_purger_cls = import_data_purger(data_purger_import)
        except DataPurgerImportException:
            logger.warning(
                "Could not import data purger %s, skipping please fix your "
                "purger imports.",
                data_purger_import,
            )
            continue

        # Some data purgers is configured to always run with DRY_RUN mode enabled.
        # Changes executed by the purger is always going to be rolled back.
        if data_purger_cls.DRY_RUN_OVERRIDE:
            logger.info(
                "Data purger %s has the DRY_RUN_OVERRIDE flag set to True, "
                "skipping tables.",
                data_purger_import,
            )
            continue

        tables |= data_purger_cls.expected_affected_models(action=action)

    return sorted(tables)
