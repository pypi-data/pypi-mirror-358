# django-data-purger

> Periodically remove data from your Django app.

## Getting Started

1. Install django-data-purger

Use Poetry to add the package

```bash
$ poetry add django-data-purger
```

2. Add `django_data_purger` to `INSTALLED_APPS`

Update your `INSTALLED_APP` setting:

```python
INSTALLED_APPS = [
    'django...',
    ...
    'django_data_purger',
]
```

3. Create a data purger in the Django app you want to clean periodically

Example:

```python
# data_purger.py
from django_data_purger.data_purger import DataPurger, PurgeResult
from app.models import DataModel
from datetime import datetime, timedelta

class PurgeDataModel(DataPurger):
    expected_delete_models = ("app.DataModel",)

    def run(self, *, now: datetime) -> list[PurgeResult]:
        old_threshold = now - timedelta(weeks=6)

        entries = DataModel.objects.filter(
            created_time__lte=old_threshold,
        )

        return self._delete_queryset_in_batch(
            entries, batch_size=DataPurger.BATCH_SIZE_LARGE
        )
```

4. Register the data purger in the `DATA_PURGERS` setting

Add the purger to your settings:

```python
DATA_PURGERS = [
    "app.data_purger.PurgeDataModel",
]
```


5. Run the management command to purge old data

Configure this command to run periodically using a scheduler like cron:

```bash
$ python manage.py run_data_purgers --force
```

## Settings

| Setting name            | Type        | Default | Description                                                |
| ----------------------- | ----------- | ------- | ---------------------------------------------------------- |
| `DATA_PURGERS`          | `list[str]` | `[]`    | Array with import strings to data purgers in your project. |

## The DataPurger Class

The DataPurger class can be used to UPDATE or DELETE models. It runs within a transaction and ensures that updates or deletions are only applied to whitelisted models.

### Update Model Instances

```python
class PurgeDataModel(DataPurger):
    expected_update_models = ("app.DataModel",)

    def run(self, *, now: datetime) -> list[PurgeResult]:
        old_threshold = now - timedelta(weeks=6)

        entries = DataModel.objects.filter(
            created_time__lte=old_threshold,
        )

        return self._update_queryset_in_batch(
            entries, updates={"is_deleted": True}, batch_size=DataPurger.BATCH_SIZE_MEDIUM
        )
```

### Delete Model Instances

```python
class PurgeDataModel(DataPurger):
    expected_delete_models = ("app.DataModel",)

    def run(self, *, now: datetime) -> list[PurgeResult]:
        old_threshold = now - timedelta(weeks=6)

        entries = DataModel.objects.filter(
            created_time__lte=old_threshold,
        )

        return self._delete_queryset_in_batch(
            entries, batch_size=DataPurger.BATCH_SIZE_LARGE
        )
```

## Planning for Model Instance Deletion

Models often depend on each other via `ForeignKey` or `ManyToManyField` relationships. It can be challenging to determine the correct order for deleting models without causing unexpected cascading deletions or errors from `on_delete=models.PROTECT`.

django-data-purger includes a tool to explore model dependencies. ✅ and 🛑 icons indicate whether a data purger for the model is already defined.

Example:

```bash
$ poetry run python manage.py calculate_model_dependencies --model app.DataModel
The following models depend on app.DataModel:
- ...

The following models depend on ...:
- ...

==============

2 models depend on app.DataModel.

==============

The models need to be deleted in the following order to safely delete app.DataModel:
(Models in the same batch can be deleted in any order.)

Batch 1:
- ✅ ...
- 🛑 ...

Batch 2:
- ✅ ...
```

## Listing Models with Enabled Data Purgers

To view all models with a configured data purger:

```bash
$ python manage.py print_data_purging_enabled_tables --action delete

- app.DataModel
```
