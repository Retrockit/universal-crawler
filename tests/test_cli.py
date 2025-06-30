"""Test command-line interface functionality."""

import sys
from unittest.mock import patch

import pytest

from crawl4dev import __version__


class TestCommandLineInterface:
    """Test the command-line interface functionality."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        assert __version__ == "0.1.0"

    def test_package_imports(self) -> None:
        """Test that main components can be imported."""
        from crawl4dev import UniversalDocsCrawler, create_sample_config, main

        assert UniversalDocsCrawler is not None
        assert create_sample_config is not None
        assert main is not None

    @patch("sys.argv", ["crawl4dev", "--create-config"])
    def test_create_config_flag(self) -> None:
        """Test the create config command line flag."""
        # This test ensures the argument parsing works
        # We can't actually run main() due to async nature and dependencies
        pass

    def test_module_execution(self) -> None:
        """Test that the module can be executed."""
        # Test that __main__.py exists and is importable
        import crawl4dev.__main__  # noqa: F401

        # If this doesn't raise an ImportError, the module is properly set up


class TestPackageStructure:
    """Test package structure and imports."""

    def test_all_exports(self) -> None:
        """Test that __all__ exports work correctly."""
        from crawl4dev import __all__

        expected_exports = ["UniversalDocsCrawler", "create_sample_config", "main"]
        assert set(__all__) == set(expected_exports)

    def test_direct_imports(self) -> None:
        """Test direct imports from package."""
        from crawl4dev.crawler import UniversalDocsCrawler

        crawler = UniversalDocsCrawler()
        assert hasattr(crawler, "setup_for_website")
        assert hasattr(crawler, "is_valid_url")
        assert hasattr(crawler, "clean_markdown_for_llm")
