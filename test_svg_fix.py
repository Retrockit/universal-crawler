#!/usr/bin/env python3
"""Test URL filtering to ensure SVG and image files are properly filtered"""

import sys

sys.path.insert(0, "src")

from crawl4dev.crawler import UniversalDocsCrawler


def test_svg_filtering() -> bool:
    """Test the specific SVG issue that was causing BrowserConfig errors"""
    print("🧪 Testing SVG and file filtering...")

    crawler = UniversalDocsCrawler()
    crawler.domain = "https://docs.ansible.com"
    crawler.url_patterns = {
        "include": [".*docs.*"],
        "exclude": [r".*/(_images|images|img|assets|static|media|files|downloads)/.*"],
    }

    # Test the exact URL that was causing the error
    problematic_urls = [
        "https://docs.ansible.com/ansible/latest/_images/ansible_inv_start.svg",
        "https://docs.ansible.com/ansible/latest/images/logo.png",
        "https://docs.ansible.com/ansible/latest/assets/style.css",
        "https://docs.ansible.com/ansible/latest/files/example.pdf",
        "https://docs.ansible.com/ansible/latest/static/script.js",
        "https://docs.ansible.com/ansible/latest/media/video.mp4",
    ]

    valid_urls = [
        "https://docs.ansible.com/ansible/latest/user_guide/",
        "https://docs.ansible.com/ansible/latest/installation_guide/index.html",
        "https://docs.ansible.com/ansible/latest/index.html",
    ]

    print("\n🚫 Testing URLs that should be FILTERED OUT:")
    all_filtered = True
    for url in problematic_urls:
        result = crawler.is_valid_url(url)
        status = "✅ FILTERED" if not result else "❌ NOT FILTERED"
        print(f"  {status}: {url}")
        if result:
            all_filtered = False

    print("\n✅ Testing URLs that should be ALLOWED:")
    all_allowed = True
    for url in valid_urls:
        result = crawler.is_valid_url(url)
        status = "✅ ALLOWED" if result else "❌ BLOCKED"
        print(f"  {status}: {url}")
        if not result:
            all_allowed = False

    success = all_filtered and all_allowed
    print(f"\n📊 Result: {'🎉 ALL TESTS PASSED' if success else '⚠️ SOME TESTS FAILED'}")
    return success


if __name__ == "__main__":
    success = test_svg_filtering()
    sys.exit(0 if success else 1)
