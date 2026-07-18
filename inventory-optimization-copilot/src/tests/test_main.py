"""Tests for main.py build entry point."""

from pathlib import Path
from unittest.mock import patch

from src.main import ensure_output_directories, main


def test_ensure_output_directories_creates_paths(tmp_path: Path, monkeypatch):
    """Required output folders should be created on demand."""
    dist = tmp_path / "dist"
    generated = tmp_path / "data" / "generated"
    monkeypatch.setattr("src.main.DIST_DIR", dist)
    monkeypatch.setattr("src.main.DATA_GENERATED_DIR", generated)

    ensure_output_directories()

    assert dist.is_dir()
    assert generated.is_dir()


def test_main_returns_success_exit_code(tmp_path: Path, monkeypatch):
    """main() should complete the full build and return 0."""
    dist = tmp_path / "dist"
    generated = tmp_path / "data" / "generated"
    workbook = dist / "Inventory_Optimization_Copilot.xlsx"

    monkeypatch.setattr("src.main.DIST_DIR", dist)
    monkeypatch.setattr("src.main.DATA_GENERATED_DIR", generated)
    monkeypatch.setattr("src.main.WORKBOOK_PATH", workbook)
    monkeypatch.setattr(
        "src.data_generation.generate_inventory.DATA_GENERATED_DIR", generated
    )

    with patch("src.main._log"):
        assert main() == 0

    assert workbook.exists()
    assert (generated / "inventory_data.csv").exists()
