"""Comprehensive test suite for crawl4dev crawler functionality."""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx  # type: ignore[import-untyped]
from httpx import Response

from crawl4dev.crawler import UniversalDocsCrawler, create_sample_config


class TestUniversalDocsCrawler:
    """Test suite for UniversalDocsCrawler class."""

    def test_init_default_config(self) -> None:
        """Test crawler initialization with default config."""
        crawler = UniversalDocsCrawler()
        assert crawler.config == {}
        assert crawler.base_url == ""
        assert crawler.domain == ""
        assert crawler.crawled_urls == set()
        assert crawler.results == []
        assert crawler.failed_urls == []

    def test_init_with_config(self) -> None:
        """Test crawler initialization with custom config."""
        config = {"max_pages": 50, "delay": 2.0}
        crawler = UniversalDocsCrawler(config)
        assert crawler.config == config

    def test_setup_for_website(self) -> None:
        """Test website setup functionality."""
        crawler = UniversalDocsCrawler()
        test_url = "https://docs.example.com/guide/"

        crawler.setup_for_website(test_url)

        assert crawler.base_url == "https://docs.example.com/guide"
        assert crawler.domain == "https://docs.example.com"
        assert "include" in crawler.url_patterns

    @pytest.mark.parametrize(
        "url,expected_patterns",
        [
            ("https://example.com/docs/", [".*docs.*"]),
            ("https://api.example.com/documentation/", [".*documentation.*"]),
            ("https://example.com/guide/", [".*guide.*"]),
            ("https://example.com/help/", [".*help.*"]),
        ],
    )
    def test_auto_detect_patterns(self, url: str, expected_patterns: list[str]) -> None:
        """Test automatic pattern detection for different URL types."""
        crawler = UniversalDocsCrawler()
        crawler.setup_for_website(url)

        include_patterns = crawler.url_patterns.get("include", [])
        for pattern in expected_patterns:
            assert any(pattern in p for p in include_patterns)

    @pytest.mark.parametrize(
        "test_url,base_domain,expected",
        [
            ("https://example.com/docs/install", "https://example.com", True),
            ("https://other.com/docs", "https://example.com", False),
            ("https://example.com/login", "https://example.com", False),
            ("https://example.com/docs/${url}", "https://example.com", False),
            ("https://example.com/docs/{{template}}", "https://example.com", False),
            ("javascript:void(0)", "https://example.com", False),
            ("mailto:test@example.com", "https://example.com", False),
            (None, "https://example.com", False),
        ],
    )
    def test_is_valid_url(self, test_url: str | None, base_domain: str, expected: bool) -> None:
        """Test URL validation functionality."""
        crawler = UniversalDocsCrawler()
        crawler.domain = base_domain
        crawler.url_patterns = {
            "include": [".*docs.*"],
            "exclude": [r".*/login.*", r".*\$\{.*\}.*", r".*\{\{.*\}\}.*"],
        }

        result = crawler.is_valid_url(test_url) if test_url else False
        assert result == expected

    def test_clean_markdown_for_llm(self) -> None:
        """Test markdown cleaning functionality."""
        crawler = UniversalDocsCrawler()

        test_markdown = """
# Main Title

Skip to content
Navigation
Menu

This is good content that should remain.

```javascript
console.log('code should remain');
```

Edit this page
Last updated: 2023-01-01
Previous | Next
"""

        cleaned = crawler.clean_markdown_for_llm(test_markdown, "https://example.com")

        # Check that good content remains
        assert "Main Title" in cleaned
        assert "good content" in cleaned
        assert "console.log" in cleaned

        # Check that UI elements are removed
        assert "Skip to content" not in cleaned
        assert "Navigation" not in cleaned
        assert "Edit this page" not in cleaned
        assert "Previous |" not in cleaned

    def test_extract_title_and_description(self) -> None:
        """Test title and description extraction."""
        crawler = UniversalDocsCrawler()

        test_markdown = """
# Getting Started Guide

This is a comprehensive guide to help you get started with the platform.

Some detailed content here.

## Installation

First, install the software...
"""

        title, description = crawler.extract_title_and_description(
            test_markdown, "https://example.com/docs/getting-started"
        )

        assert title == "Getting Started Guide"
        assert "comprehensive guide" in description

    def test_extract_title_from_url_fallback(self) -> None:
        """Test title extraction fallback to URL when no headers found."""
        crawler = UniversalDocsCrawler()

        test_markdown = "No headers here, just plain text."

        title, description = crawler.extract_title_and_description(
            test_markdown, "https://example.com/docs/installation-guide"
        )

        assert title == "Installation Guide"  # From URL path

    def test_extract_links_from_content(self) -> None:
        """Test link extraction from content."""
        crawler = UniversalDocsCrawler()
        crawler.domain = "https://example.com"
        crawler.url_patterns = {"include": [".*"], "exclude": []}

        html = (
            '<a href="/docs/guide">Guide</a><a href="https://external.com">External</a>'
        )
        markdown = "[Local Link](/docs/local) [External](https://external.com)"

        links = crawler.extract_links_from_content(
            html, markdown, "https://example.com/docs/"
        )

        # Should include relative links converted to absolute
        assert "https://example.com/docs/guide" in links
        assert "https://example.com/docs/local" in links
        # Should not include external links for this domain
        assert "https://external.com" not in links

    def test_create_site_directory_new(self) -> None:
        """Test site directory creation for new directory."""
        crawler = UniversalDocsCrawler()

        with tempfile.TemporaryDirectory() as temp_dir:
            result_dir = crawler.create_site_directory(
                temp_dir, "https://caddyserver.com/docs/"
            )

            expected_dir = os.path.join(temp_dir, "caddyserver")
            assert result_dir == expected_dir
            assert os.path.exists(result_dir)

    @pytest.mark.parametrize(
        "url,expected_site_name",
        [
            ("https://caddyserver.com/docs/", "caddyserver"),
            ("https://docs.netmaker.io/", "netmaker"),
            ("https://www.example.com/documentation/", "example"),
            ("https://api.github.com/docs/", "github"),
            ("https://opentofu.org/docs/", "opentofu"),
        ],
    )
    def test_site_name_extraction(self, url: str, expected_site_name: str) -> None:
        """Test site name extraction from various URL patterns."""
        crawler = UniversalDocsCrawler()

        with tempfile.TemporaryDirectory() as temp_dir:
            result_dir = crawler.create_site_directory(temp_dir, url)
            actual_site_name = os.path.basename(result_dir)
            assert actual_site_name == expected_site_name

    def test_save_llm_optimized_results(self) -> None:
        """Test saving results in LLM-optimized format."""
        crawler = UniversalDocsCrawler()
        crawler.base_url = "https://example.com/docs"

        # Mock results data
        results = [
            {
                "url": "https://example.com/docs/guide",
                "title": "User Guide",
                "description": "A comprehensive user guide",
                "path": "guide",
                "markdown": "# User Guide\n\nContent here",
                "content_length": 100,
                "word_count": 20,
                "crawled_at": "2023-01-01T00:00:00",
                "status_code": 200,
            }
        ]

        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("builtins.input", return_value="n"),
        ):  # Don't overwrite, create new
            files = crawler.save_llm_optimized_results(results, temp_dir)

            combined_file, metadata_file, index_file, sections_dir = files

            # Check that files were created
            assert os.path.exists(combined_file)
            assert os.path.exists(metadata_file)
            assert os.path.exists(index_file)
            assert os.path.exists(sections_dir)

            # Check file contents
            with open(combined_file) as f:
                content = f.read()
                assert "User Guide" in content
                assert "example.com" in content

    @pytest.mark.asyncio
    async def test_crawl_page_success(self) -> None:
        """Test successful page crawling."""
        crawler = UniversalDocsCrawler({"min_content_length": 50})  # Lower threshold for testing
        crawler.domain = "https://example.com"
        crawler.url_patterns = {"include": [".*"], "exclude": []}

        # Mock crawler response with longer content
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = (
            "# Test Page\n\nThis is test content with good information. "
            "This page contains detailed documentation about the testing framework "
            "and provides comprehensive examples for developers to understand "
            "the implementation details and best practices."
        )
        mock_result.html = '<a href="/test">Test Link</a>'
        mock_result.status_code = 200

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result

        page_data, links = await crawler.crawl_page(
            mock_crawler, "https://example.com/test"
        )

        assert page_data is not None
        assert page_data["title"] == "Test Page"
        assert page_data["url"] == "https://example.com/test"
        assert len(links) > 0

    @pytest.mark.asyncio
    async def test_crawl_page_failure(self) -> None:
        """Test page crawling failure handling."""
        crawler = UniversalDocsCrawler()
        crawler.domain = "https://example.com"
        crawler.url_patterns = {"include": [".*"], "exclude": []}

        # Mock failed crawler response
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.status_code = 404

        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result

        page_data, links = await crawler.crawl_page(
            mock_crawler, "https://example.com/notfound"
        )

        assert page_data is None
        assert len(links) == 0
        assert "https://example.com/notfound" in crawler.failed_urls

    @pytest.mark.asyncio
    async def test_crawl_page_invalid_url(self) -> None:
        """Test crawling with invalid URL."""
        crawler = UniversalDocsCrawler()
        crawler.domain = "https://example.com"
        crawler.url_patterns = {"include": [".*docs.*"], "exclude": []}

        mock_crawler = AsyncMock()

        # URL doesn't match include pattern
        page_data, links = await crawler.crawl_page(
            mock_crawler, "https://example.com/invalid"
        )

        assert page_data is None
        assert len(links) == 0
        # Should not call crawler for invalid URLs
        mock_crawler.arun.assert_not_called()


class TestConfigurationFunctions:
    """Test configuration-related functions."""

    def test_create_sample_config(self) -> None:
        """Test sample configuration creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # This will create a config file
                create_sample_config()

                # Check that file was created
                assert os.path.exists("crawler_config.yaml")

                # Check file content structure
                with open("crawler_config.yaml") as f:
                    content = f.read()
                    assert "crawl_settings" in content
                    assert "max_pages" in content
                    assert "url_patterns" in content

            finally:
                os.chdir(original_cwd)


class TestIntegrationScenarios:
    """Integration tests for complete workflow scenarios."""

    @pytest.mark.asyncio
    async def test_complete_workflow_mock(self) -> None:
        """Test complete crawling workflow with mocked responses."""
        crawler = UniversalDocsCrawler({"max_pages": 2, "min_content_length": 50})

        # Mock responses for different pages
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value.__aenter__.return_value = mock_crawler

            # Mock first page response with longer content
            mock_result1 = MagicMock()
            mock_result1.success = True
            mock_result1.markdown = (
                "# Home\n\nWelcome to our comprehensive documentation portal. "
                "This site contains detailed guides, tutorials, and reference materials "
                "to help you get started with our platform and understand all features."
            )
            mock_result1.html = '<a href="/guide">Guide</a>'
            mock_result1.status_code = 200

            # Mock second page response with longer content  
            mock_result2 = MagicMock()
            mock_result2.success = True
            mock_result2.markdown = (
                "# Guide\n\nThis detailed guide provides step-by-step instructions "
                "for using our platform effectively. It covers installation, configuration, "
                "and advanced usage patterns with comprehensive examples."
            )
            mock_result2.html = ""
            mock_result2.status_code = 200

            mock_crawler.arun.side_effect = [mock_result1, mock_result2]

            # Run the crawl
            results = await crawler.deep_crawl("https://example.com/docs/", max_pages=2)

            # Check results
            assert len(results) == 2
            assert results[0]["title"] == "Home"
            assert results[1]["title"] == "Guide"

    def test_error_handling_robustness(self) -> None:
        """Test that the crawler handles various error conditions gracefully."""
        crawler = UniversalDocsCrawler()

        # Test with None input
        assert not crawler.is_valid_url(None)

        # Test with empty markdown
        cleaned = crawler.clean_markdown_for_llm("", "https://example.com")
        assert cleaned == ""

        # Test with malformed URL
        assert not crawler.is_valid_url("not-a-url")

        # Test title extraction with empty content
        title, desc = crawler.extract_title_and_description(
            "", "https://example.com/test"
        )
        assert title == "Test"  # From URL
        assert desc == ""


# Performance and edge case tests
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_long_content(self) -> None:
        """Test handling of very long content."""
        crawler = UniversalDocsCrawler()

        # Create very long markdown content
        long_content = "# Title\n\n" + "This is a very long paragraph. " * 1000

        cleaned = crawler.clean_markdown_for_llm(long_content, "https://example.com")

        # Should still work and not crash
        assert "Title" in cleaned
        assert len(cleaned) > 0

    def test_special_characters_in_content(self) -> None:
        """Test handling of special characters and encoding."""
        crawler = UniversalDocsCrawler()

        special_content = """
# Title with émojis 🚀

Content with special chars: äöü, 中文, русский

[Link with special chars](./émoji-guide)
"""

        cleaned = crawler.clean_markdown_for_llm(special_content, "https://example.com")

        # Should preserve special characters
        assert "émojis" in cleaned
        assert "äöü" in cleaned
        assert "中文" in cleaned

    def test_deeply_nested_paths(self) -> None:
        """Test URL validation with deeply nested paths."""
        crawler = UniversalDocsCrawler()
        crawler.domain = "https://example.com"
        crawler.url_patterns = {"include": [".*docs.*"], "exclude": []}

        deep_url = "https://example.com/docs/api/v1/reference/endpoints/users/create"
        assert crawler.is_valid_url(deep_url)

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "",  # Empty string
            "   ",  # Whitespace only
            "not-a-url",  # Invalid format
            "ftp://example.com",  # Wrong protocol
            "https://",  # Incomplete URL
        ],
    )
    def test_invalid_url_inputs(self, invalid_input: str) -> None:
        """Test various invalid URL inputs."""
        crawler = UniversalDocsCrawler()
        crawler.domain = "https://example.com"

        assert not crawler.is_valid_url(invalid_input)
