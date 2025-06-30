import argparse
import asyncio
import json
import os
import re
import shutil
from datetime import datetime
from typing import Any
from urllib.parse import unquote, urljoin, urlparse
import yaml
from crawl4ai import AsyncWebCrawler


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
                r".*\.(pdf|zip|tar|gz|exe|dmg|pkg)$",
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

    async def crawl_page(self, crawler: Any, url: str) -> tuple[dict[str, Any] | None, set[str]]:
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

    async def deep_crawl(self, start_url: str, max_pages: int = 100) -> list[dict[str, Any]]:
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
        self, results: list[dict[str, Any]], base_output_dir: str, site_name: str | None = None
    ) -> tuple[str, str, str, str]:
        """Save results in formats optimized for LLM consumption"""
        # Create site-specific directory
        output_dir = self.create_site_directory(base_output_dir, self.base_url)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not site_name:
            # Extract clean site name from the directory name
            site_name = os.path.basename(output_dir)

        # 1. Single comprehensive markdown file for LLM context
        combined_file = os.path.join(output_dir, f"{site_name}_docs_{timestamp}.md")
        self.create_llm_markdown(results, combined_file, site_name)

        # 2. Structured sections for specific queries
        sections_dir = os.path.join(output_dir, "sections")
        self.create_sectioned_files(results, sections_dir, site_name)

        # 3. Metadata and search index
        metadata_file = os.path.join(
            output_dir, f"{site_name}_metadata_{timestamp}.json"
        )
        self.save_metadata(results, metadata_file, site_name)

        # 4. LLM-friendly index with summaries
        index_file = os.path.join(output_dir, f"{site_name}_index_{timestamp}.md")
        self.create_llm_index(results, index_file, site_name)

        return combined_file, metadata_file, index_file, sections_dir

    def create_llm_markdown(self, results: list[dict[str, Any]], filename: str, site_name: str) -> None:
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

    def save_metadata(self, results: list[dict[str, Any]], filename: str, site_name: str) -> None:
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

    def create_llm_index(self, results: list[dict[str, Any]], filename: str, site_name: str) -> None:
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


def create_sample_config() -> None:
    """Create a sample configuration file"""
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
    }

    with open("crawler_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print("📋 Sample config created: crawler_config.yaml")


async def main() -> None:
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
        "--create-config", action="store_true", help="Create sample configuration file"
    )

    args = parser.parse_args()

    if args.create_config:
        create_sample_config()
        return

    if not args.url:
        print("❌ Error: URL is required")
        print("Usage: python main.py <URL>")
        print("Example: python main.py https://caddyserver.com/docs/")
        return

    # Initialize crawler
    config = {}

    # Load configuration if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config) as f:
                if args.config.endswith((".yaml", ".yml")):
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
        combined_file, metadata_file, index_file, sections_dir = (
            crawler.save_llm_optimized_results(results, args.output_dir, site_name)
        )

        print("\n🎉 Crawling completed successfully!")
        print(f"� Site directory: {os.path.dirname(combined_file)}")
        print(f"�📄 Main file: {combined_file}")
        print(f"� Sections: {sections_dir}")
        print(f"📋 Metadata: {metadata_file}")
        print(f"📑 Index: {index_file}")

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
        print(f"• Use '{combined_file}' for comprehensive context")
        print(f"• Use files in '{sections_dir}' for specific topics")
        print(f"• Check '{index_file}' for content overview")

    else:
        print("❌ No content was crawled successfully")
        print("💡 Try adjusting the URL patterns or checking the site structure")


def cli_main() -> None:
    """Synchronous entry point for the CLI console script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
