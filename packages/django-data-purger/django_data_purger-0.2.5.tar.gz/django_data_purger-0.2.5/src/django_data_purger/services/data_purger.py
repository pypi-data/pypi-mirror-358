import logging
import time
from datetime import datetime

from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string

from django_data_purger.conf import settings
from django_data_purger.data_purger import DataPurger, PurgeResult
from django_data_purger.enums import DataPurgerAction
from django_data_purger.exceptions import DataPurgerImportException

logger = logging.getLogger(__name__)


class DryRunException(Exception):
    """
    Exception raised to rollback the transaction.

    This exception is only used to controll the roll-back,
    and it should not be exposed outside of this file.
    """


def import_data_purger(data_purger_path: str) -> type[DataPurger]:
    """Import data purger, raise exception if the import failed."""

    try:
        data_purger_cls: type[DataPurger] = import_string(data_purger_path)
        assert issubclass(data_purger_cls, DataPurger)
    except ImportError as exc:
        raise DataPurgerImportException(
            "Data purger could not be imported, check the import path."
        ) from exc
    except AssertionError as exc:
        raise DataPurgerImportException(
            "Imported object is not based on the DataPurger base class."
        ) from exc

    return data_purger_cls


def run_data_purgers(dry_run: bool = True) -> None:
    """Run data purgers defined in settings.DATA_PURGERS."""
    data_purgers_imports = settings.DATA_PURGERS

    now = timezone.now()

    results: list[PurgeResult] = []

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

        data_purger = data_purger_cls()

        results += run_data_purger(data_purger=data_purger, dry_run=dry_run, now=now)

    updated_items = sum(
        result.affected_items
        for result in results
        if result.action == DataPurgerAction.UPDATE
    )
    deleted_items = sum(
        result.affected_items
        for result in results
        if result.action == DataPurgerAction.DELETE
    )

    logger.info(
        f"Data purgers updated {updated_items:,} and deleted {deleted_items:,} items"
    )


def run_data_purger(
    *, data_purger: DataPurger, dry_run: bool, now: datetime | None = None
) -> list[PurgeResult]:
    """Run a single data purger and log the result."""
    purger_name = data_purger.__class__.__name__

    logger.info(f"Running data purger {purger_name}")

    now = now or timezone.now()

    try:
        with transaction.atomic():
            start_time = time.monotonic()

            results = data_purger.run(now=now)

            done_time = time.monotonic()

            logger.info(
                f"Data purger {purger_name} done (in {(done_time - start_time):.1f}s)"
            )

            for result in results:
                expected_affected_models = data_purger.expected_affected_models(
                    action=result.action
                )

                if result.model not in expected_affected_models:
                    raise RuntimeError(
                        f"Unexpected {result.action} on model {result.model} by "
                        f"{purger_name}, rolling back transaction"
                    )

            if dry_run:
                raise DryRunException()

            if data_purger.DRY_RUN_OVERRIDE:
                logger.info(
                    "Data purger %s has the DRY_RUN_OVERRIDE flag set to True, "
                    "changes are going to be rolled back.",
                    purger_name,
                )
                raise DryRunException()

    except DryRunException:
        pass

    if len(results) == 0:
        logger.info(f"No changes made by {purger_name}")

    for result in results:
        logger.info(
            f"Purge result from {purger_name}: "
            f"{result.model} {result.action} {result.affected_items:,} items"
        )

    return results
