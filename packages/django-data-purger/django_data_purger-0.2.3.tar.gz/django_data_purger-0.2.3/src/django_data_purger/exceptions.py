class DataPurgerException(Exception):
    """Base exception for all other exeptions raised by this library."""


class DataPurgerImportException(DataPurgerException):
    """Raised when the framework is unable to import a data purger."""


class DataPurgerInvalidConfiguration(DataPurgerException):
    """Raised when the data purger is configured incorrectly."""
