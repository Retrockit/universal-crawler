#!/usr/bin/env python3
"""
Test script to demonstrate the new directory creation functionality
"""

from urllib.parse import urlparse


def extract_site_name(url: str) -> str:
    """Extract site name from URL using the same logic as the main code"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    # Remove common prefixes and get clean site name
    site_name = domain.replace("www.", "").replace("docs.", "")

    # Handle special cases for common documentation patterns
    if "." in site_name:
        parts = site_name.split(".")
        if len(parts) >= 2:
            if parts[0] in ["docs", "documentation", "help", "api"]:
                site_name = parts[1]  # Use second part if first is docs-related
            else:
                site_name = parts[0]  # Use first part for normal domains

    # Clean site name (remove any remaining special characters)
    import re

    site_name = re.sub(r"[^\w\-]", "", site_name)

    return site_name


# Test cases
test_urls = [
    "https://caddyserver.com/docs/",
    "https://docs.netmaker.io/",
    "https://opentofu.org/docs/",
    "https://www.example.com/documentation/",
    "https://api.github.com/docs/",
]

print("🧪 Testing directory name extraction:")
print("=" * 50)

for url in test_urls:
    site_name = extract_site_name(url)
    print(f"URL: {url}")
    print(f"  → Directory: crawled_docs/{site_name}")
    print()

print("✅ Directory extraction test completed!")
