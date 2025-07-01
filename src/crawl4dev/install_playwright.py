#!/usr/bin/env python3
"""
Automatic Playwright browser installation for crawl4dev.
This script is run automatically after package installation to ensure
Playwright browsers are available without manual intervention.
"""

import subprocess
import sys


def install_playwright_browsers() -> bool:
    """Install Playwright browsers automatically."""
    print("🎭 Installing Playwright browser (Chromium)...")
    print("This is a one-time setup that may take a few minutes...")

    try:
        # Install Chromium browser for Playwright
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True,
        )

        print("✅ Playwright browser installation completed successfully!")
        print("🎉 crawl4dev is now ready to use!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        print(f"   Error output: {e.stderr}")
        print("⚠️  You may need to run 'playwright install chromium' manually.")
        return False
    except FileNotFoundError:
        print(
            "❌ Playwright not found. This should not happen if installation was successful."
        )
        print("⚠️  Please try reinstalling the package.")
        return False


def main() -> None:
    """Main entry point for the installer."""
    install_playwright_browsers()


if __name__ == "__main__":
    main()
