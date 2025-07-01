import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

from crawl4ai import AsyncWebCrawler


def check_and_install_playwright() -> bool:
    """Check if Playwright browsers are installed and install if needed."""
    try:
        # Check if chromium is available by trying to get the executable path
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from playwright.sync_api import sync_playwright; "
                "p = sync_playwright().start(); "
                "print(p.chromium.executable_path); "
                "p.stop()",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # If we get here, Playwright browsers are already installed
        if result.stdout.strip() and Path(result.stdout.strip()).exists():
            return True

    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        pass  # Browser not found, need to install

    # Install Playwright browsers
    print("🎭 First-time setup: Installing Playwright browser (Chromium)...")
    print("This is a one-time process that may take a few minutes...")

    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            timeout=300,  # 5 minutes timeout
        )

        print("✅ Playwright browser installation completed!")
        print("🎉 crawl4dev is now ready to use!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        print("⚠️  Please run 'playwright install chromium' manually.")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out. Please check your internet connection.")
        print("⚠️  Please run 'playwright install chromium' manually.")
        return False


class UniversalDocsCrawler:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.base_url = ""
        self.domain = ""
        self.crawled_urls: set[str] = set()
        self.results: list[dict[str, Any]] = []
        self.failed_urls: list[str] = []
        self.url_patterns = self.config.get("url_patterns", {})

    def setup_for_website(self, base_url: str) -> None:
        """Setup crawler for a specific website"""
        self.base_url = base_url.rstrip("/")
        parsed = urlparse(base_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.auto_detect_patterns()

    def auto_detect_patterns(self) -> None:
        """Auto-detect common documentation URL patterns"""
        path = urlparse(self.base_url).path.lower()

        if not self.url_patterns.get("include"):
            include_patterns = []
            doc_indicators = [
                "docs",
                "documentation",
                "guide",
                "manual",
                "help",
                "wiki",
                "api",
            ]

            for indicator in doc_indicators:
                if indicator in path:
                    # Create patterns that match both path segments and general occurrences
                    include_patterns.append(f".*{indicator}.*")
                    include_patterns.append(f".*/{indicator}/.*")

            if not include_patterns:
                base_path = urlparse(self.base_url).path.rstrip("/")
                if base_path:
                    include_patterns.append(f"{re.escape(base_path)}/.*")

            self.url_patterns["include"] = include_patterns

        if not self.url_patterns.get("exclude"):
            self.url_patterns["exclude"] = [
                r".*/login.*",
                r".*/register.*",
                r".*/signup.*",
                r".*/signin.*",
                r".*/cart.*",
                r".*/checkout.*",
                r".*/account.*",
                r".*/profile.*",
                r".*/admin.*",
                r".*/dashboard.*",
                r".*/settings.*",
                # File types (also handled in is_valid_url but good to have here too)
                r".*\.(pdf|zip|tar|gz|exe|dmg|pkg|png|jpg|jpeg|gif|svg|webp|ico|bmp)$",
                # Asset directories
                r".*/(_images|images|img|assets|static|media|files|downloads)/.*",
                r".*#.*",  # Skip anchor links
                r".*\?.*page=.*",  # Skip pagination
                r".*/search.*",
                r".*/tag.*",
                r".*/category.*",
                # Add patterns for template variables and invalid URLs
                r".*\$\{.*\}.*",  # Template variables like ${url}
                r".*\{\{.*\}\}.*",  # Handlebars/Mustache templates
                r".*\%7B.*\%7D.*",  # URL-encoded braces
                r".*<.*>.*",  # Angle bracket placeholders
                r".*/\*.*",  # Wildcard paths
            ]

    def is_valid_url(self, url: str | None) -> bool:
        """Check if URL should be crawled with enhanced validation"""
        if not url or not isinstance(url, str):
            return False

        # Basic URL format validation
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except Exception:
            return False

        # Skip common file types that aren't web pages
        file_extensions = [
            # Images
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".webp",
            ".ico",
            ".bmp",
            # Documents
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            # Archives
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
            # Media
            ".mp4",
            ".mp3",
            ".avi",
            ".mov",
            ".wav",
            # Code/Data
            ".json",
            ".xml",
            ".csv",
            ".txt",
            ".log",
            # Fonts
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            # Other
            ".css",
            ".js",
            ".map",
        ]

        url_lower = url.lower()
        if any(url_lower.endswith(ext) for ext in file_extensions):
            print(f"⚠️  Skipping file URL (not a webpage): {url}")
            return False

        # Decode URL-encoded characters for better pattern matching
        try:
            decoded_url = unquote(url)
        except Exception:
            decoded_url = url

        # Check for template variables and placeholders
        invalid_patterns = [
            r"\$\{.*\}",  # ${variable}
            r"\{\{.*\}\}",  # {{variable}}
            r"<[^>]*>",  # <placeholder>
            r"\*",  # wildcards
            r"undefined",  # literal undefined
            r"null",  # literal null
        ]

        if any(
            re.search(pattern, decoded_url, re.IGNORECASE)
            for pattern in invalid_patterns
        ):
            print(f"⚠️  Skipping invalid URL with template/placeholder: {url}")
            return False

        # If domain is not set yet (during testing), only check basic format
        if not self.domain:
            return True

        if not url.startswith(self.domain):
            return False

        include_patterns = self.url_patterns.get("include", [])
        if include_patterns and not any(
            re.search(pattern, url, re.IGNORECASE) for pattern in include_patterns
        ):
            return False

        exclude_patterns = self.url_patterns.get("exclude", [])
        return not (
            exclude_patterns
            and any(
                re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns
            )
        )

    def clean_markdown_for_llm(self, markdown: str, url: str) -> str:
        """Advanced markdown cleaning optimized for LLM consumption"""
        if not markdown:
            return ""

        # Step 1: Remove common UI elements and navigation
        ui_patterns = [
            r"^(Skip to|Navigation|Menu|Search|Toggle|Cookie|Privacy|Accept|Reject).*$",
            r"^(Home|Docs|Documentation|Download|GitHub|Twitter|Facebook|LinkedIn)$",
            r"^\s*\*\s*(Home|Docs|Download|Back to top|Table of contents).*$",
            r"^\s*\[.*\]\(#.*\)\s*$",  # Anchor-only links
            r"^(Edit this page|Edit on GitHub|Improve this doc).*$",
            r"^(Last updated|Last modified|Published|Created).*$",
            r"^(Share|Print|Copy link|Permalink).*$",
            r"^\s*[\*\-\+]\s*$",  # Empty list items
            r"^(Previous|Next|←|→|\<|\>)(\s|$)",  # Navigation arrows
        ]

        lines = markdown.split("\n")
        cleaned_lines = []

        # Step 2: Process each line
        for line in lines:
            original_line = line
            line = line.strip()

            # Skip empty lines (will be normalized later)
            if not line:
                cleaned_lines.append("")
                continue

            # Skip UI patterns
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in ui_patterns):
                continue

            # Skip very short lines that are likely UI elements
            if len(line) < 3 and line not in ["#", "##", "###", "####", "---", "***"]:
                continue

            # Clean up common issues
            line = original_line

            # Fix excessive indentation
            line = re.sub(r"^\s{8,}", "    ", line)

            # Clean up link text
            line = re.sub(r"\[([^\]]+)\]\(javascript:.*?\)", r"\1", line)
            line = re.sub(
                r"\[([^\]]+)\]\(#[^)]*\)", r"\1", line
            )  # Remove anchor-only links

            cleaned_lines.append(line)

        # Step 3: Rejoin and normalize
        cleaned = "\n".join(cleaned_lines)

        # Step 4: Advanced cleaning
        # Remove excessive whitespace
        cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)

        # Normalize headers (max 4 levels for LLM clarity)
        cleaned = re.sub(r"^#{5,}", "####", cleaned, flags=re.MULTILINE)

        # Remove empty code blocks
        cleaned = re.sub(r"```\s*\n\s*```", "", cleaned)

        # Clean up tables (remove empty rows)
        cleaned = re.sub(r"\|\s*\|\s*\|\s*\n", "", cleaned)

        # Remove excessive horizontal rules
        cleaned = re.sub(r"(\n---+\s*\n){2,}", "\n---\n", cleaned)

        # Step 5: Structure optimization for LLMs
        # Ensure proper spacing around headers
        cleaned = re.sub(r"\n(#{1,4}\s+[^\n]+)\n(?!\n)", r"\n\1\n\n", cleaned)

        # Ensure proper spacing around code blocks
        cleaned = re.sub(r"\n(```[^`]*```)\n(?!\n)", r"\n\1\n\n", cleaned)

        # Final cleanup
        cleaned = cleaned.strip()

        return cleaned

    def extract_title_and_description(self, markdown: str, url: str) -> tuple[str, str]:
        """Extract meaningful title and description from content"""
        lines = [line.strip() for line in markdown.split("\n") if line.strip()]

        title = ""
        description = ""

        # Try to find title from first header
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
            elif line.startswith("## ") and not title:
                title = line[3:].strip()
                break

        # Fallback: extract from URL
        if not title:
            path_parts = urlparse(url).path.strip("/").split("/")
            if path_parts and path_parts[-1]:
                title = path_parts[-1].replace("-", " ").replace("_", " ").title()
            else:
                title = "Documentation"

        # Extract description from first substantial paragraph
        in_code_block = False
        for line in lines:
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            if not in_code_block and not line.startswith("#") and len(line) > 50:
                # Clean up the line for description
                desc_line = re.sub(
                    r"\[([^\]]+)\]\([^)]+\)", r"\1", line
                )  # Remove links
                desc_line = re.sub(r"[*_`]", "", desc_line)  # Remove formatting
                if len(desc_line) > 30:
                    description = (
                        desc_line[:200] + "..." if len(desc_line) > 200 else desc_line
                    )
                    break

        return title, description

    def extract_links_from_content(
        self, html: str, markdown: str, base_url: str
    ) -> set[str]:
        """Extract relevant links from page content with better validation"""
        links = set()

        # Extract from markdown links
        markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown)
        for _text, url in markdown_links:
            if not url.startswith(("http", "//", "mailto:", "tel:")):
                try:
                    full_url = urljoin(base_url, url)
                    if self.is_valid_url(full_url):
                        links.add(full_url)
                except Exception:
                    print(f"⚠️  Invalid URL found in markdown: {url}")
                    continue

        # Extract from HTML href attributes (more comprehensive)
        html_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        for url in html_links:
            if not url.startswith(("http", "//", "mailto:", "tel:", "javascript:")):
                try:
                    full_url = urljoin(base_url, url)
                    if self.is_valid_url(full_url):
                        links.add(full_url)
                except Exception:
                    print(f"⚠️  Invalid URL found in HTML: {url}")
                    continue

        return links

    async def crawl_page(
        self, crawler: Any, url: str
    ) -> tuple[dict[str, Any] | None, set[str]]:
        """Crawl a single page with enhanced error handling"""
        try:
            print(f"🔄 Crawling: {url}")

            # Pre-validate URL before attempting to crawl
            if not self.is_valid_url(url):
                print(f"⚠️  Skipping invalid URL: {url}")
                return None, set()

            # Configure crawling parameters
            crawl_params = {
                "url": url,
                "word_count_threshold": self.config.get("min_word_count", 20),
                "remove_overlay_elements": True,
                "clean_html": True,
                "delay_before_return_html": self.config.get("delay", 1.5),
                "excluded_tags": self.config.get(
                    "excluded_tags",
                    [
                        "nav",
                        "header",
                        "footer",
                        "aside",
                        "script",
                        "style",
                        "noscript",
                        "iframe",
                        "form",
                        "button",
                    ],
                ),
                # Add timeout settings
                "page_timeout": self.config.get("page_timeout", 30000),  # 30 seconds
            }

            # Add CSS selector if specified
            if self.config.get("content_selector"):
                crawl_params["css_selector"] = self.config["content_selector"]

            result = await crawler.arun(**crawl_params)

            if result.success and result.markdown:
                # Clean the markdown for LLM consumption
                cleaned_markdown = self.clean_markdown_for_llm(result.markdown, url)

                if len(cleaned_markdown) > self.config.get("min_content_length", 100):
                    # Extract title and description
                    title, description = self.extract_title_and_description(
                        cleaned_markdown, url
                    )

                    # Create structured path
                    parsed_url = urlparse(url)
                    path_parts = [p for p in parsed_url.path.strip("/").split("/") if p]
                    structured_path = "/".join(path_parts) if path_parts else "home"

                    page_data = {
                        "url": url,
                        "title": title,
                        "description": description,
                        "path": structured_path,
                        "markdown": cleaned_markdown,
                        "raw_html": result.html,  # Store raw HTML for later saving
                        "content_length": len(cleaned_markdown),
                        "word_count": len(cleaned_markdown.split()),
                        "crawled_at": datetime.now().isoformat(),
                        "status_code": getattr(result, "status_code", 200),
                    }

                    # Extract links for further crawling
                    found_links = self.extract_links_from_content(
                        result.html, result.markdown, url
                    )

                    print(
                        f"✅ Success: {title[:50]}... ({len(cleaned_markdown)} chars, {len(found_links)} links)"
                    )
                    return page_data, found_links
                else:
                    print(
                        f"⚠️  Skipped: {url} (insufficient content: {len(cleaned_markdown)} chars)"
                    )
            else:
                print(
                    f"❌ Failed: {url} (Status: {getattr(result, 'status_code', 'Unknown')})"
                )
                self.failed_urls.append(url)

        except Exception as e:
            error_msg = str(e)
            if (
                "net::ERR_HTTP_RESPONSE_CODE_FAILURE" in error_msg
                or "template" in error_msg.lower()
            ):
                print(f"⚠️  Skipping problematic URL: {url} (Template/Invalid URL)")
            else:
                print(f"💥 Error crawling {url}: {error_msg}")
            self.failed_urls.append(url)

        return None, set()

    async def deep_crawl(
        self, start_url: str, max_pages: int = 100
    ) -> list[dict[str, Any]]:
        """Perform deep crawl of the website with better error handling"""
        self.setup_for_website(start_url)

        print("🚀 Starting deep crawl...")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🌐 Domain: {self.domain}")
        print(f"📊 Max pages: {max_pages}")
        print(
            f"🎯 Include patterns: {self.url_patterns.get('include', 'Auto-detected')}"
        )

        urls_to_crawl = {start_url}

        # Configure crawler with better error handling
        crawler_config = {
            "verbose": self.config.get("verbose", True),
            "headless": self.config.get("headless", True),
            "browser_type": self.config.get("browser_type", "chromium"),
            "headers": self.config.get(
                "headers",
                {
                    "User-Agent": "Mozilla/5.0 (compatible; Documentation Crawler; +https://github.com/crawler)"
                },
            ),
        }

        async with AsyncWebCrawler(**crawler_config) as crawler:
            while urls_to_crawl and len(self.results) < max_pages:
                current_url = urls_to_crawl.pop()

                if current_url in self.crawled_urls:
                    continue

                self.crawled_urls.add(current_url)

                # Crawl the current page
                page_data, found_links = await self.crawl_page(crawler, current_url)

                if page_data:
                    self.results.append(page_data)

                # Add newly found links to crawl queue with validation
                new_links = found_links - self.crawled_urls
                valid_new_links = [
                    link for link in new_links if self.is_valid_url(link)
                ]
                for link in valid_new_links[:10]:  # Limit new links per page
                    if len(self.results) < max_pages:
                        urls_to_crawl.add(link)

                # Respectful delay
                await asyncio.sleep(self.config.get("crawl_delay", 0.5))

        print("\n🎉 Crawling complete!")
        print(f"✅ Successfully crawled: {len(self.results)} pages")
        print(f"❌ Failed: {len(self.failed_urls)} pages")

        # Show some failed URLs for debugging (limit to 5)
        if self.failed_urls:
            print("\n⚠️  Sample failed URLs:")
            for url in self.failed_urls[:5]:
                print(f"   • {url}")
            if len(self.failed_urls) > 5:
                print(f"   ... and {len(self.failed_urls) - 5} more")

        return self.results

    def save_llm_optimized_results(
        self,
        results: list[dict[str, Any]],
        base_output_dir: str,
        site_name: str | None = None,
        enable_chunking: bool = False,
        chunk_size: int = 4000,
        save_html: bool = False,
        save_individual_markdown: bool = True,
        enable_sections: bool = False,
        enable_combined: bool = False,
        enable_index: bool = False,
    ) -> tuple[
        str | None, str, str | None, str | None, str | None, str | None, str | None
    ]:
        """Save results in formats optimized for LLM consumption"""
        # Create site-specific directory
        output_dir = self.create_site_directory(base_output_dir, self.base_url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not site_name:
            # Extract clean site name from the directory name
            site_name = os.path.basename(output_dir)

        # 1. Single comprehensive markdown file for LLM context (optional)
        combined_file = None
        if enable_combined:
            combined_file = os.path.join(output_dir, f"{site_name}_docs_{timestamp}.md")
            self.create_llm_markdown(results, combined_file, site_name)

        # 2. Structured sections for specific queries (optional)
        sections_dir = None
        if enable_sections:
            sections_dir = os.path.join(output_dir, "sections")
            self.create_sectioned_files(results, sections_dir, site_name)

        # 3. Metadata and search index
        metadata_file = os.path.join(
            output_dir, f"{site_name}_metadata_{timestamp}.json"
        )
        self.save_metadata(results, metadata_file, site_name)

        # 4. LLM-friendly index with summaries (optional)
        index_file = None
        if enable_index:
            index_file = os.path.join(output_dir, f"{site_name}_index_{timestamp}.md")
            self.create_llm_index(results, index_file, site_name)

        # 5. Raw HTML files in separate directory (optional)
        html_dir = None
        if save_html:
            html_dir = os.path.join(output_dir, "html")
            self.save_raw_html_files(results, html_dir, site_name)

        # 6. Individual markdown files in separate directory (optional)
        markdown_dir = None
        if save_individual_markdown:
            markdown_dir = os.path.join(output_dir, "markdown")
            self.save_individual_markdown_files(results, markdown_dir, site_name)

        # 7. LLM-optimized content chunks (if enabled)
        chunks_dir = None
        if enable_chunking:
            chunks, chunk_manifest = self.create_chunks(results, chunk_size, site_name)
            chunks_dir = self.save_chunks(chunks, chunk_manifest, output_dir, site_name)

        return (
            combined_file,
            metadata_file,
            index_file,
            sections_dir,
            chunks_dir,
            html_dir,
            markdown_dir,
        )

    def create_llm_markdown(
        self, results: list[dict[str, Any]], filename: str, site_name: str
    ) -> None:
        """Create a comprehensive markdown file optimized for LLM understanding"""
        # Sort results logically
        sorted_results = sorted(
            results,
            key=lambda x: (
                x["path"].count("/"),  # Depth first
                x["path"],  # Then alphabetically
                -x["word_count"],  # Then by content richness
            ),
        )

        content = f"# {site_name.title()} Documentation\n\n"
        content += f"**Source:** {self.base_url}\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Total Pages:** {len(results)}\n"
        content += f"**Total Words:** {sum(r['word_count'] for r in results):,}\n"
        content += "**Coverage:** Complete documentation crawl\n\n"

        # Add table of contents
        content += "## Table of Contents\n\n"
        for i, result in enumerate(sorted_results, 1):
            safe_anchor = re.sub(r"[^\w\-]", "-", result["title"].lower())
            content += f"{i}. [{result['title']}](#{safe_anchor})\n"
        content += "\n---\n\n"

        # Add content sections
        for i, result in enumerate(sorted_results, 1):
            # Create clear section headers
            content += f"# {i}. {result['title']}\n\n"

            # Add metadata for context
            content += f"**Path:** `{result['path']}`\n"
            if result["description"]:
                content += f"**Description:** {result['description']}\n"
            content += f"**Word Count:** {result['word_count']}\n\n"

            # Add the cleaned content
            content += result["markdown"]

            # Clear section separator
            content += "\n\n" + "=" * 100 + "\n\n"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📄 LLM-optimized markdown saved: {filename}")
        print(
            f"📊 Total size: {len(content):,} characters ({len(content.split()):,} words)"
        )

    def create_sectioned_files(
        self, results: list[dict[str, Any]], sections_dir: str, site_name: str
    ) -> None:
        """Create individual section files for targeted queries"""
        os.makedirs(sections_dir, exist_ok=True)

        # Group by main sections
        sections: dict[str, list[dict]] = {}
        for result in results:
            path_parts = result["path"].split("/")
            main_section = path_parts[0] if path_parts[0] else "home"

            if main_section not in sections:
                sections[main_section] = []
            sections[main_section].append(result)

        for section_name, pages in sections.items():
            safe_name = re.sub(r"[^\w\-_.]", "_", section_name)
            section_file = os.path.join(sections_dir, f"{safe_name}.md")

            content = f"# {site_name.title()} - {section_name.title()}\n\n"
            content += f"**Section:** {section_name}\n"
            content += f"**Pages:** {len(pages)}\n"
            content += f"**Total Words:** {sum(p['word_count'] for p in pages):,}\n\n"

            for page in sorted(pages, key=lambda x: x["path"]):
                content += f"## {page['title']}\n\n"
                if page["description"]:
                    content += f"*{page['description']}*\n\n"
                content += page["markdown"]
                content += "\n\n---\n\n"

            with open(section_file, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"📁 Section files created in: {sections_dir}")
        print(f"📊 Sections: {', '.join(sections.keys())}")

    def save_metadata(
        self, results: list[dict[str, Any]], filename: str, site_name: str
    ) -> None:
        """Save comprehensive metadata for search and analysis"""
        metadata = {
            "site_info": {
                "name": site_name,
                "base_url": self.base_url,
                "domain": self.domain,
                "crawled_at": datetime.now().isoformat(),
                "crawler_version": "2.0",
            },
            "crawl_stats": {
                "total_pages": len(results),
                "total_words": sum(r["word_count"] for r in results),
                "total_characters": sum(r["content_length"] for r in results),
                "failed_urls": len(self.failed_urls),
                "success_rate": len(results)
                / (len(results) + len(self.failed_urls))
                * 100
                if (len(results) + len(self.failed_urls)) > 0
                else 0,
            },
            "content_analysis": {
                "avg_words_per_page": sum(r["word_count"] for r in results)
                / len(results)
                if results
                else 0,
                "longest_page": max(results, key=lambda x: x["word_count"])["title"]
                if results
                else "",
                "sections": list({r["path"].split("/")[0] for r in results}),
                "total_sections": len({r["path"].split("/")[0] for r in results}),
            },
            "pages": results,
            "failed_urls": self.failed_urls,
            "config_used": self.config,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📋 Metadata saved: {filename}")

    def create_llm_index(
        self, results: list[dict[str, Any]], filename: str, site_name: str
    ) -> None:
        """Create an LLM-friendly index with summaries"""
        content = f"# {site_name.title()} Documentation Index\n\n"
        content += "This index provides a structured overview of all documentation content, optimized for LLM understanding and navigation.\n\n"

        # Statistics
        content += "## Overview\n\n"
        content += f"- **Total Pages:** {len(results)}\n"
        content += f"- **Total Words:** {sum(r['word_count'] for r in results):,}\n"
        content += f"- **Average Words per Page:** {sum(r['word_count'] for r in results) // len(results) if results else 0:,}\n"
        content += f"- **Source:** {self.base_url}\n\n"

        # Group by sections
        sections: dict[str, list[dict]] = {}
        for result in results:
            section = result["path"].split("/")[0] if result["path"] else "home"
            if section not in sections:
                sections[section] = []
            sections[section].append(result)

        content += "## Sections\n\n"
        for section_name, pages in sorted(sections.items()):
            content += f"### {section_name.title()}\n\n"
            content += f"**Pages:** {len(pages)} | **Words:** {sum(p['word_count'] for p in pages):,}\n\n"

            for page in sorted(pages, key=lambda x: (-x["word_count"], x["title"])):
                content += f"#### {page['title']}\n"
                content += f"- **Path:** `{page['path']}`\n"
                content += f"- **Words:** {page['word_count']:,}\n"
                if page["description"]:
                    content += f"- **Summary:** {page['description']}\n"
                content += f"- **URL:** {page['url']}\n\n"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📑 LLM index created: {filename}")

    def save_raw_html_files(
        self, results: list[dict[str, Any]], html_dir: str, site_name: str
    ) -> None:
        """Save raw HTML files for each crawled page"""
        os.makedirs(html_dir, exist_ok=True)

        for i, result in enumerate(results, 1):
            # Create safe filename from URL path
            url_path = urlparse(result["url"]).path
            if url_path == "/" or not url_path:
                safe_filename = "index.html"
            else:
                # Convert path to safe filename
                safe_path = url_path.strip("/").replace("/", "_")
                safe_filename = re.sub(r"[^\w\-_.]", "_", safe_path)
                if not safe_filename.endswith(".html"):
                    safe_filename += ".html"

            # Add number prefix for uniqueness and ordering
            numbered_filename = f"{i:03d}_{safe_filename}"
            html_file = os.path.join(html_dir, numbered_filename)

            # Create HTML content with metadata header
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{result["title"]}</title>
    <!-- Crawl Metadata -->
    <meta name="crawl-url" content="{result["url"]}">
    <meta name="crawl-path" content="{result["path"]}">
    <meta name="crawl-timestamp" content="{result["crawled_at"]}">
    <meta name="crawl-word-count" content="{result["word_count"]}">
    <meta name="crawl-description" content="{result.get("description", "").replace('"', "&quot;")}">
</head>
<body>
    <!-- Original HTML content from crawl -->
    {result.get("raw_html", "<p>No HTML content available</p>")}
</body>
</html>"""

            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

        print(f"📄 Raw HTML files saved in: {html_dir}")
        print(f"📊 Created {len(results)} HTML files")

    def save_individual_markdown_files(
        self, results: list[dict[str, Any]], markdown_dir: str, site_name: str
    ) -> None:
        """Save individual markdown files for each crawled page"""
        os.makedirs(markdown_dir, exist_ok=True)

        for i, result in enumerate(results, 1):
            # Create safe filename from title or URL path
            if result["title"] and result["title"] != "Documentation":
                safe_title = re.sub(r"[^\w\-_\s]", "", result["title"])
                safe_title = re.sub(r"\s+", "_", safe_title.strip())[:50]
                safe_filename = f"{safe_title}.md"
            else:
                # Fallback to URL path
                url_path = urlparse(result["url"]).path
                if url_path == "/" or not url_path:
                    safe_filename = "index.md"
                else:
                    safe_path = url_path.strip("/").replace("/", "_")
                    safe_filename = re.sub(r"[^\w\-_.]", "_", safe_path) + ".md"

            # Add number prefix for uniqueness and ordering
            numbered_filename = f"{i:03d}_{safe_filename}"
            md_file = os.path.join(markdown_dir, numbered_filename)

            # Create markdown content with frontmatter
            escaped_description = result.get("description", "").replace('"', '\\"')
            md_content = f"""---
title: "{result["title"]}"
url: "{result["url"]}"
path: "{result["path"]}"
description: "{escaped_description}"
word_count: {result["word_count"]}
crawled_at: "{result["crawled_at"]}"
status_code: {result.get("status_code", 200)}
---

# {result["title"]}

**Source URL:** [{result["url"]}]({result["url"]})
**Path:** `{result["path"]}`
**Crawled:** {result["crawled_at"][:10]}
**Words:** {result["word_count"]:,}

{f"**Description:** {result['description']}" if result.get("description") else ""}

---

{result["markdown"]}
"""

            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)

        print(f"📝 Individual markdown files saved in: {markdown_dir}")
        print(f"📊 Created {len(results)} markdown files")

    def create_site_directory(self, base_output_dir: str, url: str) -> str:
        """Create a site-specific directory with overwrite handling"""
        # Extract site name from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove common prefixes and get clean site name
        site_name = domain.replace("www.", "").replace("docs.", "")

        # Handle special cases for common documentation patterns
        if "." in site_name:
            parts = site_name.split(".")
            if len(parts) >= 2:
                # For domains like caddyserver.com -> caddyserver
                # For domains like docs.netmaker.io -> netmaker
                # For domains like opentofu.org -> opentofu
                if parts[0] in ["docs", "documentation", "help", "api"]:
                    site_name = parts[1]  # Use second part if first is docs-related
                else:
                    site_name = parts[0]  # Use first part for normal domains

        # Clean site name (remove any remaining special characters)
        site_name = re.sub(r"[^\w\-]", "", site_name)

        # Create the site-specific directory path
        site_dir = os.path.join(base_output_dir, site_name)

        # Check if directory exists
        if os.path.exists(site_dir):
            print(f"\n📁 Directory already exists: {site_dir}")
            print("📄 This directory contains previous crawl data.")

            while True:
                response = (
                    input("❓ Do you want to overwrite it? (y/n): ").lower().strip()
                )

                if response in ["y", "yes"]:
                    print(f"🗑️ Removing existing directory: {site_dir}")
                    shutil.rmtree(site_dir)
                    break
                elif response in ["n", "no"]:
                    # Create a new directory with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    site_name_new = f"{site_name}_{timestamp}"
                    site_dir = os.path.join(base_output_dir, site_name_new)
                    print(f"📂 Creating new directory: {site_dir}")
                    break
                else:
                    print("⚠️ Please enter 'y' for yes or 'n' for no.")

        # Create the directory
        os.makedirs(site_dir, exist_ok=True)
        print(f"✅ Using directory: {site_dir}")

        return site_dir

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation: 1 token ≈ 4 characters)"""
        return len(text) // 4

    def split_text_semantically(
        self, text: str, max_tokens: int, min_tokens: int = 1000
    ) -> list[str]:
        """Split text at semantic boundaries while respecting token limits"""
        chunks = []
        current_chunk = ""

        # Split by double newlines first (paragraph breaks)
        paragraphs = text.split("\n\n")

        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed the limit
            test_chunk = (
                current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            )

            if self.estimate_tokens(test_chunk) <= max_tokens:
                current_chunk = test_chunk
            else:
                # If current chunk has enough content, save it
                if current_chunk and self.estimate_tokens(current_chunk) >= min_tokens:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # If paragraph is too long by itself, split by sentences
                    if self.estimate_tokens(paragraph) > max_tokens:
                        # Split by periods, but keep code blocks intact
                        if "```" in paragraph:
                            # Handle code blocks specially
                            chunks.append(
                                current_chunk.strip()
                            ) if current_chunk else None
                            chunks.append(paragraph)
                            current_chunk = ""
                        else:
                            # Split by sentences
                            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                            for sentence in sentences:
                                test_chunk = (
                                    current_chunk + " " + sentence
                                    if current_chunk
                                    else sentence
                                )
                                if self.estimate_tokens(test_chunk) <= max_tokens:
                                    current_chunk = test_chunk
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                    current_chunk = sentence
                    else:
                        # Paragraph fits, but combined with current chunk it doesn't
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = paragraph

        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk.strip())

        return [chunk for chunk in chunks if chunk.strip()]

    def create_chunks(
        self,
        results: list[dict[str, Any]],
        chunk_size: int = 4000,
        site_name: str = "docs",
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Create LLM-optimized chunks from crawled results"""
        chunks: list[dict[str, Any]] = []
        chunk_manifest: dict[str, Any] = {
            "site_name": site_name,
            "source_url": self.base_url,
            "generated_at": datetime.now().isoformat(),
            "total_chunks": 0,
            "chunk_size_target": chunk_size,
            "chunks": [],
        }

        # Sort results for logical grouping
        sorted_results = sorted(
            results,
            key=lambda x: (
                x["path"].count("/"),  # Depth first
                x["path"],  # Then alphabetically
            ),
        )

        current_chunk_content = ""
        current_chunk_topics: list[str] = []
        current_chunk_pages: list[dict[str, Any]] = []
        chunk_number = 1

        for result in sorted_results:
            page_content = f"\n\n## {result['title']}\n\n"
            page_content += f"**URL:** {result['url']}\n"
            page_content += f"**Path:** `{result['path']}`\n\n"
            page_content += result["markdown"]

            # Check if adding this page would exceed chunk size
            test_content = current_chunk_content + page_content
            estimated_tokens = self.estimate_tokens(test_content)

            if estimated_tokens <= chunk_size or not current_chunk_content:
                # Add to current chunk (add header if this is the first content)
                if not current_chunk_content:
                    current_chunk_content = f"# {site_name.title()} Documentation - Chunk {chunk_number}\n\n"
                    current_chunk_content += f"**Source**: {self.base_url}\n"
                    current_chunk_content += (
                        f"**Chunk**: {chunk_number} of [total_chunks_placeholder]\n"
                    )

                current_chunk_content += page_content
                current_chunk_topics.append(result["title"])
                current_chunk_pages.append(
                    {
                        "url": result["url"],
                        "title": result["title"],
                        "word_count": result["word_count"],
                    }
                )
            else:
                # Save current chunk and start new one
                if current_chunk_content:
                    chunk_info = self._create_chunk_info(
                        chunk_number,
                        current_chunk_content,
                        current_chunk_topics,
                        current_chunk_pages,
                        site_name,
                    )
                    chunks.append(chunk_info)
                    chunk_manifest["chunks"].append(
                        {
                            "chunk_number": chunk_number,
                            "filename": chunk_info["filename"],
                            "topics": ", ".join(
                                current_chunk_topics[:3]
                            ),  # First 3 topics
                            "page_count": len(current_chunk_pages),
                            "word_count": sum(
                                p["word_count"] for p in current_chunk_pages
                            ),
                            "estimated_tokens": self.estimate_tokens(
                                current_chunk_content
                            ),
                        }
                    )

                # Start new chunk
                chunk_number += 1
                current_chunk_content = (
                    f"# {site_name.title()} Documentation - Chunk {chunk_number}\n\n"
                )
                current_chunk_content += f"**Source**: {self.base_url}\n"
                current_chunk_content += (
                    f"**Chunk**: {chunk_number} of [total_chunks_placeholder]\n"
                )
                current_chunk_content += page_content
                current_chunk_topics = [result["title"]]
                current_chunk_pages = [
                    {
                        "url": result["url"],
                        "title": result["title"],
                        "word_count": result["word_count"],
                    }
                ]

        # Add final chunk
        if current_chunk_content:
            chunk_info = self._create_chunk_info(
                chunk_number,
                current_chunk_content,
                current_chunk_topics,
                current_chunk_pages,
                site_name,
            )
            chunks.append(chunk_info)
            chunk_manifest["chunks"].append(
                {
                    "chunk_number": chunk_number,
                    "filename": chunk_info["filename"],
                    "topics": ", ".join(current_chunk_topics[:3]),
                    "page_count": len(current_chunk_pages),
                    "word_count": sum(p["word_count"] for p in current_chunk_pages),
                    "estimated_tokens": self.estimate_tokens(current_chunk_content),
                }
            )

        # Update total chunks count and fix placeholders
        chunk_manifest["total_chunks"] = len(chunks)
        for chunk in chunks:
            chunk["content"] = chunk["content"].replace(
                "[total_chunks_placeholder]", str(len(chunks))
            )

        return chunks, chunk_manifest

    def _create_chunk_info(
        self,
        chunk_number: int,
        content: str,
        topics: list[str],
        pages: list[dict[str, Any]],
        site_name: str,
    ) -> dict[str, Any]:
        """Create chunk information dictionary"""
        # Create safe filename
        main_topic = topics[0] if topics else "content"
        safe_topic = re.sub(r"[^\w\-_]", "-", main_topic.lower())[:30]
        filename = f"{site_name}_chunk_{chunk_number:02d}_{safe_topic}.md"

        # Add navigation context to content
        enhanced_content = content
        if chunk_number > 1:
            enhanced_content += "\n\n---\n**Navigation Context**:\n"
            enhanced_content += f"- Previous: [Chunk {chunk_number - 1}]\n"
            enhanced_content += f"- Next: [Chunk {chunk_number + 1}] (if available)\n"
            enhanced_content += (
                "- Index: See chunk_manifest.json for complete topic map\n"
            )

        return {
            "chunk_number": chunk_number,
            "filename": filename,
            "content": enhanced_content,
            "topics": topics,
            "pages": pages,
            "word_count": sum(p["word_count"] for p in pages),
            "estimated_tokens": self.estimate_tokens(content),
        }

    def save_chunks(
        self,
        chunks: list[dict[str, Any]],
        manifest: dict[str, Any],
        output_dir: str,
        site_name: str,
    ) -> str:
        """Save chunks to individual files and create manifest"""
        chunks_dir = os.path.join(output_dir, "chunks")
        os.makedirs(chunks_dir, exist_ok=True)

        # Save individual chunk files
        for chunk in chunks:
            chunk_path = os.path.join(chunks_dir, chunk["filename"])
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(chunk["content"])

        # Save manifest
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manifest_filename = f"{site_name}_chunk_manifest_{timestamp}.json"
        manifest_path = os.path.join(chunks_dir, manifest_filename)

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return chunks_dir


def create_sample_config() -> None:
    """Create a sample configuration file"""
    import yaml

    config = {
        "crawl_settings": {
            "max_pages": 100,
            "delay": 1.5,
            "crawl_delay": 0.5,
            "min_word_count": 20,
            "min_content_length": 100,
            "headless": True,
            "verbose": True,
            "page_timeout": 30000,  # 30 seconds
        },
        "content_extraction": {
            "content_selector": "main, .content, .docs-content, article, .markdown-body, .documentation",
            "excluded_tags": [
                "nav",
                "header",
                "footer",
                "aside",
                "script",
                "style",
                "noscript",
                "iframe",
                "form",
                "button",
            ],
        },
        "url_patterns": {
            "include": [
                # Will be auto-detected if not specified
            ],
            "exclude": [
                r".*/login.*",
                r".*/register.*",
                r".*/signup.*",
                r".*/cart.*",
                r".*/checkout.*",
                r".*/account.*",
                r".*\.(pdf|zip|tar|gz|exe|dmg|pkg)$",
                r".*#.*",
                r".*\?.*page=.*",
                r".*\$\{.*\}.*",  # Template variables
                r".*\{\{.*\}\}.*",  # Handlebars templates
            ],
        },
        "output": {
            "site_name": "auto",  # Will be auto-detected
            "output_dir": "crawled_docs",  # Base directory - site-specific subdirectories will be created
        },
        "chunk_settings": {
            "chunk_size": 4000,  # Target tokens per chunk
            "min_chunk_size": 1000,  # Minimum chunk size
            "max_chunk_size": 6000,  # Maximum chunk size
            "preserve_code_blocks": True,  # Don't split code examples
            "include_navigation": True,  # Add prev/next chunk references
            "semantic_splitting": True,  # Split at headers, not arbitrary points
        },
    }

    with open("crawler_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print("📋 Sample config created: crawler_config.yaml")


async def main() -> None:
    import argparse
    import json

    import yaml

    parser = argparse.ArgumentParser(
        description="Universal Documentation Crawler for LLM Training"
    )
    parser.add_argument("url", nargs="?", help="Base URL to start crawling from")
    parser.add_argument("--config", "-c", help="Configuration file (YAML or JSON)")
    parser.add_argument(
        "--max-pages", "-m", type=int, default=50, help="Maximum pages to crawl"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="crawled_docs",
        help="Base output directory (site-specific subdirectories will be created)",
    )
    parser.add_argument("--site-name", "-n", help="Site name for output files")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=4000,
        help="Target token count per chunk for LLM optimization (default: 4000)",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Disable saving raw HTML files (saves storage space)",
    )
    parser.add_argument(
        "--enable-html",
        action="store_true",
        help="Enable saving raw HTML files (disabled by default)",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Disable saving individual markdown files",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Only save raw HTML files and main documentation (skips individual markdown files)",
    )
    parser.add_argument(
        "--enable-chunking",
        action="store_true",
        help="Enable automatic chunking for LLM optimization (disabled by default)",
    )
    parser.add_argument(
        "--enable-sections",
        action="store_true",
        help="Enable creation of section files for targeted queries (disabled by default)",
    )
    parser.add_argument(
        "--enable-combined",
        action="store_true",
        help="Enable creation of combined documentation file (disabled by default)",
    )
    parser.add_argument(
        "--enable-index",
        action="store_true",
        help="Enable creation of index/overview file (disabled by default)",
    )
    parser.add_argument(
        "--create-config", action="store_true", help="Create sample configuration file"
    )

    args = parser.parse_args()

    if args.create_config:
        create_sample_config()
        return

    if not args.url:
        print("❌ Error: URL is required")
        print()
        print("🚀 Usage: crawl4dev <URL> [OPTIONS]")
        print()
        print("📖 Simple example:")
        print("   crawl4dev https://docs.python.org/3/")
        print()
        print("🔧 With options:")
        print(
            "   crawl4dev https://docs.python.org/3/ --max-depth 2 --output-dir my-docs"
        )
        print()
        print("💡 For help: crawl4dev --help")
        return

    # Check and install Playwright browsers if needed
    if not check_and_install_playwright():
        print("❌ Failed to setup Playwright browsers. Cannot continue.")
        print("💡 Try running 'playwright install chromium' manually.")
        return

    # Initialize crawler
    config = {}

    # Load configuration if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config) as f:
                if args.config.endswith((".yaml", ".yml")):
                    import yaml

                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            print(f"📋 Loaded config from {args.config}")
        except Exception as e:
            print(f"⚠️  Could not load config: {e}")

    # Override config with command line arguments
    if args.max_pages:
        config["max_pages"] = args.max_pages

    crawler = UniversalDocsCrawler(config)

    print("🌐 Universal Documentation Crawler")
    print(f"🎯 Target: {args.url}")
    print(f"📊 Max pages: {args.max_pages}")
    print(f"📁 Output: {args.output_dir}")

    # Perform the crawl
    results = await crawler.deep_crawl(args.url, args.max_pages)

    if results:
        # Save results
        site_name = args.site_name or urlparse(args.url).netloc.replace("www.", "")
        enable_chunking = args.enable_chunking
        enable_sections = args.enable_sections
        enable_combined = args.enable_combined
        enable_index = args.enable_index

        # Determine output format options
        save_html = (
            args.enable_html and not args.no_html
        )  # Only save HTML if explicitly enabled
        save_individual_markdown = not args.no_markdown

        # Handle --html-only flag (override individual markdown saving)
        if args.html_only:
            save_individual_markdown = False
            save_html = True

        (
            combined_file,
            metadata_file,
            index_file,
            sections_dir,
            chunks_dir,
            html_dir,
            markdown_dir,
        ) = crawler.save_llm_optimized_results(
            results,
            args.output_dir,
            site_name,
            enable_chunking=enable_chunking,
            chunk_size=args.chunk_size,
            save_html=save_html,
            save_individual_markdown=save_individual_markdown,
            enable_sections=enable_sections,
            enable_combined=enable_combined,
            enable_index=enable_index,
        )

        print("\n🎉 Crawling completed successfully!")
        # Use output_dir or derive from metadata_file since those are always created
        site_directory = os.path.dirname(metadata_file)
        print(f"📁 Site directory: {site_directory}")

        if combined_file:
            print(f"📄 Combined file: {combined_file}")
        else:
            print("📄 Combined file: Disabled (use --enable-combined to enable)")

        if sections_dir:
            print(f"📂 Sections: {sections_dir}")
        else:
            print("📂 Sections: Disabled (use --enable-sections to enable)")

        print(f"📋 Metadata: {metadata_file}")

        if index_file:
            print(f"📑 Index: {index_file}")
        else:
            print("📑 Index: Disabled (use --enable-index to enable)")

        if html_dir:
            print(f"🌐 Raw HTML: {html_dir}")
        else:
            print("🌐 Raw HTML: Disabled (use --enable-html to enable)")

        if markdown_dir:
            print(f"📝 Individual Markdown: {markdown_dir}")
        else:
            print("📝 Individual Markdown: Disabled (use --no-markdown to re-enable)")

        if chunks_dir:
            print(f"🤖 LLM Chunks: {chunks_dir}")
            # Count chunk files
            chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".md")]
            print(f"   Created {len(chunk_files)} optimized chunks for LLM consumption")
        else:
            print("🤖 LLM Chunks: Disabled (use --enable-chunking to enable)")

        # Show statistics
        total_words = sum(r["word_count"] for r in results)
        print("\n📊 Final Statistics:")
        print(f"✅ Pages crawled: {len(results)}")
        print(f"📝 Total words: {total_words:,}")
        print(
            f"📄 Average words/page: {total_words // len(results) if results else 0:,}"
        )
        print(
            f"🎯 Success rate: {len(results) / (len(results) + len(crawler.failed_urls)) * 100 if (len(results) + len(crawler.failed_urls)) > 0 else 100:.1f}%"
        )

        print("\n🤖 LLM Usage Tips:")

        if combined_file:
            if chunks_dir:
                print(
                    f"• Use chunks in '{chunks_dir}' for LLM consumption (size: {args.chunk_size} tokens)"
                )
                print(
                    f"• Use '{combined_file}' for comprehensive context (may be too large for some LLMs)"
                )
            else:
                print(f"• Use '{combined_file}' for comprehensive context")
        else:
            print(
                "• Individual markdown files in 'markdown/' directory are optimized for LLM consumption"
            )
            if chunks_dir:
                print(
                    f"• Use chunks in '{chunks_dir}' for LLM consumption (size: {args.chunk_size} tokens)"
                )
            else:
                print(
                    "• Enable chunking with --enable-chunking for LLM-optimized content"
                )

        if markdown_dir:
            print(
                f"• Individual markdown files in '{markdown_dir}' for granular access"
            )

        if sections_dir:
            print(f"• Use files in '{sections_dir}' for specific topics")
        else:
            print("• Enable sections with --enable-sections for topic-specific files")

        if index_file:
            print(f"• Check '{index_file}' for content overview")
        else:
            print("• Enable index with --enable-index for content overview")

        if html_dir:
            print(f"• Raw HTML files available in '{html_dir}' for debugging/analysis")
        if not html_dir:
            print("• Enable HTML output with --enable-html for debugging/analysis")
        if chunks_dir:
            print("• Each chunk is self-contained and ready for copy-paste into LLMs")

    else:
        print("❌ No content was crawled successfully")
        print("💡 Try adjusting the URL patterns or checking the site structure")


def cli_main() -> None:
    """Synchronous entry point for the CLI console script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
