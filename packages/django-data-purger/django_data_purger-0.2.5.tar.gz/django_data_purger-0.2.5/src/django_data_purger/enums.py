from django.db.models import TextChoices


class DataPurgerAction(TextChoices):
    """Action to perform on the model by a data purger."""

    UPDATE = "update"
    DELETE = "delete"
