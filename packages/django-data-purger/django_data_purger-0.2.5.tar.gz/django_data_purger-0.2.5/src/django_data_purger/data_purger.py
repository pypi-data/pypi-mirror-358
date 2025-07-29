from collections import defaultdict
from datetime import datetime
from typing import Any, ClassVar

from django.db.models import QuerySet
from pydantic import BaseModel, TypeAdapter, ValidationError

from .enums import DataPurgerAction
from .exceptions import DataPurgerInvalidConfiguration
from .utils import queryset_in_batches_non_slicing


class PurgeResult(BaseModel):
    model: str
    action: DataPurgerAction
    affected_items: int


class PurgeUpdateResult(PurgeResult):
    action: DataPurgerAction = DataPurgerAction.UPDATE


class PurgeDeleteResult(PurgeResult):
    action: DataPurgerAction = DataPurgerAction.DELETE


class DataPurger:
    BATCH_SIZE_LARGE = 500_000
    BATCH_SIZE_MEDIUM = 10_000
    BATCH_SIZE_SMALL = 500

    DRY_RUN_OVERRIDE: ClassVar[bool] = False

    expected_update_models: ClassVar[tuple[str, ...]] = ()
    expected_delete_models: ClassVar[tuple[str, ...]] = ()

    def run(self, *, now: datetime) -> list[PurgeResult]:
        raise NotImplementedError("Subclasses must implement run")

    def _update_queryset_in_batch(
        self,
        queryset: QuerySet[Any],
        *,
        batch_size: int = BATCH_SIZE_MEDIUM,
        updates: dict[str, Any],
        affected_rows_limit: int | None = None,
    ) -> list[PurgeResult]:
        """Update queryset in batches, return a list of PurgeResults."""
        results: list[PurgeResult] = []

        for batch in queryset_in_batches_non_slicing(queryset, chunk_size=batch_size):
            results += self._update_queryset(batch, updates)

            if affected_rows_limit and (
                sum(result.affected_items for result in results) >= affected_rows_limit
            ):
                break

        # Some models may have multiple purge results in the result list.
        # Group them together by model name for better output.
        queryset_result: dict[str, int] = defaultdict(int)

        for result in results:
            queryset_result[result.model] += result.affected_items

        return [
            PurgeUpdateResult(model=model, affected_items=affected_items)
            for model, affected_items in queryset_result.items()
        ]

    def _delete_queryset_in_batch(
        self,
        queryset: QuerySet[Any],
        *,
        batch_size: int = BATCH_SIZE_MEDIUM,
        affected_rows_limit: int | None = None,
    ) -> list[PurgeResult]:
        """Delete queryset in batches, return a list of PurgeResults."""
        results: list[PurgeResult] = []

        for batch in queryset_in_batches_non_slicing(queryset, chunk_size=batch_size):
            results += self._delete_queryset(batch)

            if affected_rows_limit and (
                sum(result.affected_items for result in results) >= affected_rows_limit
            ):
                break

        # Some models may have multiple purge results in the result list.
        # Group them together by model name for better output.
        queryset_result: dict[str, int] = defaultdict(int)

        for result in results:
            queryset_result[result.model] += result.affected_items

        return [
            PurgeDeleteResult(model=model, affected_items=affected_items)
            for model, affected_items in queryset_result.items()
        ]

    def _update_queryset(
        self, queryset: QuerySet[Any], updates: dict[str, Any]
    ) -> list[PurgeResult]:
        """Update items in querset and return a list of PurgeResults."""
        affected_models = queryset.update(**updates)

        result: list[PurgeResult] = []

        result.append(
            PurgeUpdateResult(
                model=queryset.model._meta.label,
                affected_items=affected_models,
            )
        )

        return result

    def _delete_queryset(self, queryset: QuerySet[Any]) -> list[PurgeResult]:
        """Delete items in querset and return a list of PurgeResults."""
        _, affected_models = queryset.delete()

        result: list[PurgeResult] = []

        for model, affected_items in affected_models.items():
            result.append(PurgeDeleteResult(model=model, affected_items=affected_items))

        return result

    #
    # Expected models
    #

    @classmethod
    def expected_affected_models(cls, action: DataPurgerAction) -> set[str]:
        """Return a set with the expected models affected by this data purger."""

        attr = f"expected_{action.value}_models"

        if not hasattr(cls, attr):
            raise DataPurgerInvalidConfiguration(
                f"Data purger {cls} does not have the {attr} configured."
            )

        expected_models = getattr(cls, attr)

        try:
            TypeAdapter(set[str] | list[str] | tuple[str]).validate_python(
                expected_models
            )
        except ValidationError as exc:
            raise DataPurgerInvalidConfiguration(
                f"The {attr} attr on the data purger {cls} has to be a list of strings."
            ) from exc

        return set(getattr(cls, attr))
