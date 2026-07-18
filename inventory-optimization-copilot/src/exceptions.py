"""Custom exceptions for the Inventory Optimization Copilot build pipeline."""

from __future__ import annotations

from pathlib import Path


class BuildProcessError(Exception):
    """Base class for build pipeline failures."""


class WorkbookBuildError(BuildProcessError):
    """Raised when workbook assembly or save fails."""

    def __init__(self, message: str, *, output_path: Path | None = None) -> None:
        self.output_path = output_path
        super().__init__(message)


class WorkbookValidationError(BuildProcessError):
    """Raised when a saved workbook fails structural or content validation."""

    def __init__(self, message: str, *, path: Path | None = None) -> None:
        self.path = path
        super().__init__(message)
