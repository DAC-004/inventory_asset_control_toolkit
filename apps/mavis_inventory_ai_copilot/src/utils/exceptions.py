"""Custom application exceptions."""


class InventoryCopilotError(Exception):
    """Base exception for the inventory co-pilot application."""


class DataLoadError(InventoryCopilotError):
    """Raised when inventory data cannot be loaded."""


class DataValidationError(InventoryCopilotError):
    """Raised when required validation fails."""


class MissingColumnsError(DataValidationError):
    """Raised when required columns are missing from the dataset."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Missing required columns: {', '.join(missing)}")
