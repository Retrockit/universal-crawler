import asyncio
from crawl4ai import AsyncWebCrawler
import re
from urllib.parse import urljoin, urlparse
import os
from datetime import datetime
import json
import yaml
import argparse
from typing import Set, List, Dict, Optional, Tuple


class UniversalDocsCrawler:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.base_url = ""
        self.domain = ""
        self.crawled_urls: Set[str] = set()
        self.results: List[Dict] = []
        self.failed_urls: List[str] = []
        self.url_patterns = self.config.get("url_patterns", {})

    def setup_for_website(self, base_url: str):
        """Setup crawler for a specific website"""
        self.base_url = base_url.rstrip("/")
        parsed = urlparse(base_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.auto_detect_patterns()

    def auto_detect_patterns(self):
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
            ]

    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        if not url.startswith(self.domain):
            return False

        include_patterns = self.url_patterns.get("include", [])
        if include_patterns and not any(
            re.search(pattern, url, re.IGNORECASE) for pattern in include_patterns
        ):
            return False

        exclude_patterns = self.url_patterns.get("exclude", [])
        if exclude_patterns and any(
            re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns
        ):
            return False

        return True

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

    def extract_title_and_description(self, markdown: str, url: str) -> Tuple[str, str]:
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
    ) -> Set[str]:
        """Extract relevant links from page content"""
        links = set()

        # Extract from markdown links
        markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown)
        for text, url in markdown_links:
            if not url.startswith(("http", "//", "mailto:", "tel:")):
                full_url = urljoin(base_url, url)
                if self.is_valid_url(full_url):
                    links.add(full_url)

        # Extract from HTML href attributes (more comprehensive)
        html_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        for url in html_links:
            if not url.startswith(("http", "//", "mailto:", "tel:", "javascript:")):
                full_url = urljoin(base_url, url)
                if self.is_valid_url(full_url):
                    links.add(full_url)

        return links

    async def crawl_page(self, crawler, url: str) -> Tuple[Optional[Dict], Set[str]]:
        """Crawl a single page with advanced content extraction"""
        try:
            print(f"🔄 Crawling: {url}")

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
            print(f"💥 Error crawling {url}: {str(e)}")
            self.failed_urls.append(url)

        return None, set()

    async def deep_crawl(self, start_url: str, max_pages: int = 100) -> List[Dict]:
        """Perform deep crawl of the website"""
        self.setup_for_website(start_url)

        print(f"🚀 Starting deep crawl...")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🌐 Domain: {self.domain}")
        print(f"📊 Max pages: {max_pages}")
        print(
            f"🎯 Include patterns: {self.url_patterns.get('include', 'Auto-detected')}"
        )

        urls_to_crawl = {start_url}

        # Configure crawler
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

                # Add newly found links to crawl queue
                new_links = found_links - self.crawled_urls
                for link in list(new_links)[:10]:  # Limit new links per page
                    if len(self.results) < max_pages:
                        urls_to_crawl.add(link)

                # Respectful delay
                await asyncio.sleep(self.config.get("crawl_delay", 0.5))

        print(f"\n🎉 Crawling complete!")
        print(f"✅ Successfully crawled: {len(self.results)} pages")
        print(f"❌ Failed: {len(self.failed_urls)} pages")

        return self.results

    def save_llm_optimized_results(
        self, results: List[Dict], output_dir: str, site_name: Optional[str] = None
    ):
        """Save results in formats optimized for LLM consumption"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not site_name:
            site_name = urlparse(self.base_url).netloc.replace("www.", "")

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

    def create_llm_markdown(self, results: List[Dict], filename: str, site_name: str):
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
        content += f"**Coverage:** Complete documentation crawl\n\n"

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
        self, results: List[Dict], sections_dir: str, site_name: str
    ):
        """Create individual section files for targeted queries"""
        os.makedirs(sections_dir, exist_ok=True)

        # Group by main sections
        sections: Dict[str, List[Dict]] = {}
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

    def save_metadata(self, results: List[Dict], filename: str, site_name: str):
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
                "sections": list(set(r["path"].split("/")[0] for r in results)),
                "total_sections": len(set(r["path"].split("/")[0] for r in results)),
            },
            "pages": results,
            "failed_urls": self.failed_urls,
            "config_used": self.config,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📋 Metadata saved: {filename}")

    def create_llm_index(self, results: List[Dict], filename: str, site_name: str):
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
        sections: Dict[str, List[Dict]] = {}
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


def create_sample_config():
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
            ],
        },
        "output": {
            "site_name": "auto",  # Will be auto-detected
            "output_dir": "crawled_docs",
        },
    }

    with open("crawler_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print("📋 Sample config created: crawler_config.yaml")


async def main():
    parser = argparse.ArgumentParser(
        description="Universal Documentation Crawler for LLM Training"
    )
    parser.add_argument("url", nargs="?", help="Base URL to start crawling from")
    parser.add_argument("--config", "-c", help="Configuration file (YAML or JSON)")
    parser.add_argument(
        "--max-pages", "-m", type=int, default=50, help="Maximum pages to crawl"
    )
    parser.add_argument(
        "--output-dir", "-o", default="crawled_docs", help="Output directory"
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
        print("Usage: python universal_docs_crawler.py <URL>")
        print("Example: python universal_docs_crawler.py https://caddyserver.com/docs/")
        return

    # Initialize crawler
    config = {}

    # Load configuration if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, "r") as f:
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

    print(f"🌐 Universal Documentation Crawler")
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

        print(f"\n🎉 Crawling completed successfully!")
        print(f"📄 Main file: {combined_file}")
        print(f"📁 Sections: {sections_dir}")
        print(f"📋 Metadata: {metadata_file}")
        print(f"📑 Index: {index_file}")

        # Show statistics
        total_words = sum(r["word_count"] for r in results)
        print(f"\n📊 Final Statistics:")
        print(f"✅ Pages crawled: {len(results)}")
        print(f"📝 Total words: {total_words:,}")
        print(
            f"📄 Average words/page: {total_words // len(results) if results else 0:,}"
        )
        print(
            f"🎯 Success rate: {len(results) / (len(results) + len(crawler.failed_urls)) * 100 if (len(results) + len(crawler.failed_urls)) > 0 else 100:.1f}%"
        )

        print(f"\n🤖 LLM Usage Tips:")
        print(f"• Use '{combined_file}' for comprehensive context")
        print(f"• Use files in '{sections_dir}' for specific topics")
        print(f"• Check '{index_file}' for content overview")

    else:
        print("❌ No content was crawled successfully")
        print("💡 Try adjusting the URL patterns or checking the site structure")


if __name__ == "__main__":
    asyncio.run(main())
