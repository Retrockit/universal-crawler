#!/usr/bin/env python3
"""
Quick test for URL filtering fixes
"""

import sys

sys.path.insert(0, "src")

from crawl4dev.crawler import UniversalDocsCrawler


def test_url_filtering():
    """Test that image URLs and other file types are properly filtered"""
    print("🧪 Testing URL filtering for file types...")

    crawler = UniversalDocsCrawler()
    crawler.domain = "https://docs.ansible.com"
    crawler.url_patterns = {
        "include": [".*docs.*"],
        "exclude": [r".*/(_images|images|img|assets|static|media|files|downloads)/.*"],
    }

    test_cases = [
        # Should be REJECTED (file types)
        (
            "https://docs.ansible.com/ansible/latest/_images/ansible_inv_start.svg",
            False,
        ),
        ("https://docs.ansible.com/ansible/latest/images/logo.png", False),
        ("https://docs.ansible.com/ansible/latest/assets/style.css", False),
        ("https://docs.ansible.com/ansible/latest/files/example.pdf", False),
        ("https://docs.ansible.com/ansible/latest/downloads/package.zip", False),
        # Should be ACCEPTED (documentation pages)
        ("https://docs.ansible.com/ansible/latest/user_guide/", True),
        ("https://docs.ansible.com/ansible/latest/installation_guide/", True),
        ("https://docs.ansible.com/ansible/latest/index.html", True),
    ]

    all_passed = True

    for url, expected in test_cases:
        result = crawler.is_valid_url(url)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {url} -> {result} (expected {expected})")
        if result != expected:
            all_passed = False

    print(f"\n📊 Test Results: {'🎉 ALL PASSED' if all_passed else '⚠️ SOME FAILED'}")
    return all_passed


if __name__ == "__main__":
    success = test_url_filtering()
    sys.exit(0 if success else 1)
