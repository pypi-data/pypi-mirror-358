from typing import Generator, TypeVar

from django.db.models import Model, QuerySet

TModel = TypeVar("TModel", bound=Model)


def queryset_in_batches_non_slicing(
    queryset: QuerySet[TModel], chunk_size: int = 1000
) -> Generator[QuerySet[TModel], None, None]:
    """
    Iterate over a Django queryset that is ordered by primary key.

    Does not slice the queryset and filters naively on upper and lower bounds
    using pk and chunk size. This allows queryset operations to be performed
    such as `.update()` and `.delete()`.
    """

    queryset = queryset.order_by("pk")

    first_element = queryset.first()

    # Empty queryset
    if first_element is None:
        return

    pk = max(first_element.pk - 1, 0)

    last_element = queryset.last()

    assert last_element is not None

    while pk < last_element.pk:
        prev_pk = pk
        pk = pk + chunk_size
        queryset_to_yield = queryset.filter(pk__gt=prev_pk, pk__lte=pk)
        yield queryset_to_yield
