# Universal Documentation Crawler

A powerful, intelligent web crawler designed specifically for extracting clean, LLM-optimized markdown from documentation websites. Built with Python and Crawl4AI, this tool automatically discovers, crawls, and processes documentation sites to create structured markdown files perfect for AI training and knowledge bases.

## 🌟 Features

### 🎯 **Smart Documentation Detection**

- **Auto-pattern recognition** - Automatically detects documentation URL patterns
- **Intelligent link discovery** - Finds related pages through content analysis
- **Template variable filtering** - Skips invalid URLs with placeholders like `${variable}`
- **Breadth-first crawling** - Systematic exploration of documentation structure

### 🧹 **LLM-Optimized Content Processing**

- **Advanced markdown cleaning** - Removes navigation, UI elements, and clutter
- **Content normalization** - Standardizes headers, spacing, and formatting
- **Context preservation** - Maintains document structure and relationships
- **Multi-format output** - Combined files, individual sections, and metadata

### 🛡️ **Robust & Respectful Crawling**

- **Error handling** - Gracefully handles failed requests and invalid URLs
- **Rate limiting** - Built-in delays to respect server resources
- **Timeout management** - Configurable timeouts for problematic pages
- **Progress tracking** - Real-time crawling status and statistics

### 📊 **Comprehensive Output**

- **Combined markdown** - Single file with all documentation for LLM context
- **Sectioned files** - Individual files organized by topic/section
- **Metadata tracking** - JSON files with crawl statistics and page info
- **Content analysis** - Word counts, success rates, and section breakdowns

## 🚀 Quick Start

### Step-by-Step Setup

**Important**: Follow these steps exactly in the order shown. Each step must complete successfully before moving to the next one.

#### Prerequisites (Required First)

You must have these installed before continuing:

1. **Python 3.11 or newer**

   - Check by running: `python --version`
   - If you see a version like `Python 3.11.x` or higher, you're ready
   - If not, download from: https://python.org/downloads/

2. **Internet connection** (required for downloading and crawling)

3. **At least 500MB free disk space** (for browser files and crawled content)

#### Choose Your Installation Method

⚠️ **IMPORTANT BROWSER SETUP**: This tool requires browser automation via Playwright. Each installation method includes specific steps to install browser files. **Do not skip the browser installation steps** or the crawler will fail with "browser not found" errors.

**Pick ONE method below that matches your needs:**

#### Method 1: Simple Installation (Recommended for Most Users)

**When to use this**: You want to use the crawler as a command-line tool and don't plan to modify the code.

**Using pipx (Most Reliable):**

Step 1: Install pipx (if you don't have it)

```bash
python -m pip install --user pipx
```

Step 2: Add pipx to your system PATH (one-time setup)

```bash
pipx ensurepath
```

Step 3: Restart your terminal/command prompt completely

- Close your terminal window
- Open a new terminal window
- This ensures the PATH changes take effect

Step 4: Install the crawler

```bash
pipx install git+https://github.com/yourusername/universal-docs-crawler.git
```

Step 5: Install required browser files

```bash
# Install playwright in the same environment
pipx inject crawl4dev playwright

# Install browser binaries using the injected playwright
pipx runpip crawl4dev install playwright
pipx run --spec crawl4dev playwright install chromium
```

Step 6: Test that it works

```bash
crawl4dev --help
```

You should see help text appear. If you get an error, go back and check each step.

**Using uvx (Alternative Method):**

This method downloads everything automatically but may be slower:

```bash
# Option A: Install and run in one command (includes browser setup)
uvx --from git+https://github.com/yourusername/universal-docs-crawler.git crawl4dev https://fastapi.tiangolo.com/

# Option B: Install for repeated use
uvx install git+https://github.com/yourusername/universal-docs-crawler.git

# Install browser files (required for Option B)
uvx run --from git+https://github.com/yourusername/universal-docs-crawler.git playwright install chromium

# Test it works
crawl4dev --help
```

#### Method 2: Development Installation (For Programmers)

**When to use this**: You want to modify the code, contribute to the project, or understand how it works.

**Using uv (Recommended for Development):**

Step 1: Install uv (if you don't have it)

```bash
pip install uv
```

Step 2: Download the code

```bash
git clone https://github.com/yourusername/universal-docs-crawler.git
cd universal-docs-crawler
```

Step 3: Install with development tools

```bash
uv sync --extra dev
```

Step 4: Install browser files

```bash
uv run playwright install chromium
```

Step 5: Test that it works

```bash
uv run crawl4dev --help
```

**Using pip with virtual environment (Traditional Method):**

Step 1: Download the code

```bash
git clone https://github.com/yourusername/universal-docs-crawler.git
cd universal-docs-crawler
```

Step 2: Create isolated environment

```bash
python -m venv .venv
```

Step 3: Activate the environment

```bash
# On Linux/Mac:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

Step 4: Install the crawler

```bash
pip install -e .
pip install playwright
```

Step 5: Install browser files

```bash
playwright install chromium
```

Step 6: Test that it works

```bash
crawl4dev --help
```

#### Method 3: Use as Python Library (For Python Programs)

**When to use this**: You want to use the crawler inside your own Python programs.

Step 1: Install as a library

```bash
pip install git+https://github.com/yourusername/universal-docs-crawler.git
```

Step 2: Install browser files

```bash
playwright install chromium
```

Step 3: Test in Python

```python
import asyncio
from crawl4dev import UniversalDocsCrawler

async def test_crawler():
    crawler = UniversalDocsCrawler()
    results = await crawler.deep_crawl('https://httpbin.org/html', max_pages=1)
    print(f"Successfully crawled {len(results)} pages")

# Run the test
asyncio.run(test_crawler())
```

### Verify Your Installation

**These tests confirm everything is working correctly:**

Test 1: Check the help command

```bash
crawl4dev --help
```

**Expected result**: You should see usage instructions and options.

Test 2: Create a sample configuration

```bash
crawl4dev --create-config
```

**Expected result**: A file named `crawler_config.yaml` should be created.

Test 3: Test crawling (quick test)

```bash
crawl4dev https://httpbin.org/html --max-pages 1
```

**Expected result**: The crawler should download and process one page successfully.

## 📚 How to Use the Crawler

### Basic Usage Examples

**All examples below assume you completed the installation successfully.**

#### Example 1: Crawl a Small Documentation Site

```bash
crawl4dev https://httpbin.org/html --max-pages 5
```

**What this does:**

- Downloads up to 5 pages from the website
- Saves results in a folder called `crawled_docs/`
- Creates several files with the extracted content

#### Example 2: Crawl with Custom Settings

```bash
crawl4dev https://fastapi.tiangolo.com/ --max-pages 20 --output-dir my_docs --site-name fastapi
```

**What each option means:**

- `--max-pages 20`: Download at most 20 pages
- `--output-dir my_docs`: Save files in a folder called `my_docs/`
- `--site-name fastapi`: Name the output files with "fastapi" prefix

#### Example 3: Use a Configuration File

Step 1: Create a configuration file

```bash
crawl4dev --create-config
```

This creates a file called `crawler_config.yaml`

Step 2: Edit the file (optional)
Open `crawler_config.yaml` in a text editor and change settings if needed.

Step 3: Use the configuration

```bash
crawl4dev https://docs.example.com/ --config crawler_config.yaml
```

### Command Reference

**Basic command structure:**

```bash
crawl4dev [WEBSITE_URL] [OPTIONS]
```

**Available options:**

| Option                | What it does                     | Example                      |
| --------------------- | -------------------------------- | ---------------------------- |
| `--max-pages NUMBER`  | Limit how many pages to download | `--max-pages 50`             |
| `--output-dir FOLDER` | Choose where to save files       | `--output-dir my_folder`     |
| `--site-name NAME`    | Choose a name for output files   | `--site-name my_site`        |
| `--config FILE`       | Use settings from a file         | `--config my_config.yaml`    |
| `--create-config`     | Create a sample settings file    | (no additional value needed) |
| `--help`              | Show all available options       | (no additional value needed) |

### Using the Python API

**If you want to use the crawler in your Python programs:**

#### Basic Python Example

```python
import asyncio
from crawl4dev import UniversalDocsCrawler

async def crawl_site():
    # Create a crawler instance
    crawler = UniversalDocsCrawler()

    # Crawl a website (this will take some time)
    results = await crawler.deep_crawl('https://fastapi.tiangolo.com/', max_pages=10)

    # Show what we got
    print(f"Successfully crawled {len(results)} pages")
    for page in results:
        print(f"- {page['title']} ({page['word_count']} words)")

# Run the crawler
asyncio.run(crawl_site())
```

#### Advanced Python Example with Configuration

```python
import asyncio
from crawl4dev import UniversalDocsCrawler

async def advanced_crawl():
    # Configuration settings
    config = {
        'max_pages': 25,
        'delay': 2.0,  # Wait 2 seconds between pages
        'min_word_count': 50,  # Skip pages with fewer than 50 words
        'headless': True,  # Don't show browser window
        'verbose': True   # Show detailed progress
    }

    # Create crawler with configuration
    crawler = UniversalDocsCrawler(config)

    # Crawl the site
    results = await crawler.deep_crawl('https://docs.python.org/3/', max_pages=25)

    # Save results to files
    if results:
        output_files = crawler.save_llm_optimized_results(
            results,
            base_output_dir='my_crawled_docs',
            site_name='python_docs'
        )
        print(f"Results saved to: {output_files[0]}")

    return results

# Run it
results = asyncio.run(advanced_crawl())
```

## � Troubleshooting

### Common Installation Issues

#### Problem: "playwright not found" or "Browser not installed"

**Solution:**

```bash
# Make sure Playwright browsers are installed
playwright install chromium

# For pipx installations - install playwright first, then browsers
pipx inject crawl4dev playwright
pipx run --spec crawl4dev playwright install chromium

# For development setups
uv run playwright install chromium
```

#### Problem: "Permission denied" or "Command not found"

**Solution:**

```bash
# For pipx installations, ensure pipx bin directory is in PATH
pipx ensurepath
source ~/.bashrc  # or restart terminal

# For uvx, make sure uvx is available
pip install --user uv
```

#### Problem: "Module 'crawl4ai' not found"

**Solution:**

```bash
# Verify installation
pip list | grep crawl4ai

# Reinstall if missing
pip install crawl4ai

# For development setup
uv sync
```

#### Problem: Crawling fails or times out

**Solution:**

```bash
# Try with increased timeout and fewer pages
crawl4dev https://example.com --max-pages 5 --page-timeout 60000

# Check if site blocks automated browsers
crawl4dev https://example.com --headless false

# Use configuration file for fine-tuning
crawl4dev --create-config
# Edit crawler_config.yaml and use: crawl4dev https://example.com --config crawler_config.yaml
```

### Performance Tips

#### For Large Documentation Sites

```bash
# Start with a small number to test
crawl4dev https://docs.example.com --max-pages 10

# Gradually increase for full crawl
crawl4dev https://docs.example.com --max-pages 200 --delay 2.0
```

#### For Slow or Unreliable Sites

```yaml
# In crawler_config.yaml
crawl_settings:
  delay: 3.0 # Longer delay between pages
  page_timeout: 60000 # 60 second timeout
  crawl_delay: 2.0 # Longer delay between requests
```

#### Memory Usage Optimization

```bash
# For very large sites, process in chunks
crawl4dev https://docs.example.com --max-pages 50 --output-dir chunk1
crawl4dev https://docs.example.com --max-pages 50 --output-dir chunk2
# ... combine results manually
```

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this README for detailed configuration
- **Logs**: Use `--verbose` flag for detailed crawling information
- **Configuration**: Use `--create-config` to see all available options

### Core Dependencies

- **crawl4ai**: The main web crawling library (automatically installs playwright)
- **pyyaml**: For configuration file support
- **asyncio**: Built into Python 3.7+ (for async crawling)

### What Crawl4AI Includes

- **Playwright**: Browser automation (Chrome, Firefox, Safari)
- **Content extraction**: HTML to markdown conversion
- **JavaScript rendering**: Handles dynamic content
- **Request management**: Headers, cookies, sessions

### Browser Requirements

Crawl4AI uses Playwright, which requires actual browser binaries:

- **Chromium**: ~170MB download (recommended)
- **Firefox**: ~80MB download
- **WebKit**: ~60MB download

## 📖 Usage Guide

### Command Line Options

```bash
python main.py <URL> [OPTIONS]
```

| Option            | Short | Description                    | Default        |
| ----------------- | ----- | ------------------------------ | -------------- |
| `--max-pages`     | `-m`  | Maximum pages to crawl         | 50             |
| `--output-dir`    | `-o`  | Output directory               | `crawled_docs` |
| `--site-name`     | `-n`  | Custom site name for files     | Auto-detected  |
| `--config`        | `-c`  | Configuration file (YAML/JSON) | None           |
| `--create-config` |       | Create sample config file      |                |

### Examples

#### Basic Documentation Crawling

```bash
# Crawl Python documentation
uv run main.py https://docs.python.org/3/

# Crawl Kubernetes docs with custom output
uv run main.py https://kubernetes.io/docs/ --output-dir k8s_docs --max-pages 100

# Crawl Next.js documentation
uv run main.py https://nextjs.org/docs --site-name nextjs
```

#### Advanced Usage with Configuration

```bash
# Create sample configuration
uv run main.py --create-config

# Use configuration file
uv run main.py https://docs.example.com/ --config crawler_config.yaml
```

#### Real-World Examples

```bash
# Large documentation sites
uv run main.py https://kubernetes.io/docs/ --max-pages 200 --output-dir k8s
uv run main.py https://docs.aws.amazon.com/ --max-pages 500 --output-dir aws

# Framework documentation
uv run main.py https://react.dev/ --max-pages 50 --site-name react
uv run main.py https://vuejs.org/guide/ --max-pages 30 --site-name vue

# API documentation
uv run main.py https://docs.github.com/en/rest --max-pages 100 --site-name github-api
```

## ⚙️ Configuration

### Sample Configuration File

Create a `crawler_config.yaml` file:

```yaml
crawl_settings:
  max_pages: 100
  delay: 1.5
  crawl_delay: 0.5
  min_word_count: 20
  min_content_length: 100
  headless: true
  verbose: true
  page_timeout: 30000

content_extraction:
  content_selector: "main, .content, .docs-content, article, .markdown-body"
  excluded_tags:
    - nav
    - header
    - footer
    - aside
    - script
    - style
    - noscript
    - iframe
    - form
    - button

url_patterns:
  include:
    # Auto-detected if not specified
    # - ".*\\/docs\\/.*"
    # - ".*\\/guide\\/.*"
  exclude:
    - ".*/login.*"
    - ".*/register.*"
    - ".*/cart.*"
    - ".*\\.(pdf|zip|tar|gz)$"
    - ".*#.*"
    - ".*\\$\\{.*\\}.*" # Template variables

output:
  site_name: "auto"
  output_dir: "crawled_docs"
```

### Configuration Options

#### Crawl Settings

- `max_pages`: Maximum number of pages to crawl (default: 50)
- `delay`: Delay before extracting content from each page (default: 1.5s)
- `crawl_delay`: Delay between page requests (default: 0.5s)
- `min_word_count`: Minimum words required to process a page (default: 20)
- `min_content_length`: Minimum content length in characters (default: 100)
- `page_timeout`: Page load timeout in milliseconds (default: 30000)
- `headless`: Run browser in headless mode (default: true)
- `verbose`: Enable detailed logging (default: true)

#### Content Extraction

- `content_selector`: CSS selectors for main content areas
- `excluded_tags`: HTML tags to exclude from content

#### URL Patterns

- `include`: Regex patterns for URLs to include (auto-detected if empty)
- `exclude`: Regex patterns for URLs to exclude

#### Site-Specific Configurations

**For GitBook sites:**

```yaml
content_extraction:
  content_selector: ".page-inner, .markdown-section"
  excluded_tags: [".gitbook-link", ".page-header"]
```

**For Docusaurus sites:**

```yaml
content_extraction:
  content_selector: ".markdown, article"
  excluded_tags: [".theme-doc-sidebar", ".navbar"]
```

**For Sphinx documentation:**

```yaml
content_extraction:
  content_selector: ".document, .body"
  excluded_tags: [".sphinxsidebar", ".related"]
```

## 📁 Output Structure

The crawler generates a comprehensive set of files:

```
crawled_docs/
├── sitename_docs_20241201_143022.md      # Combined markdown file
├── sitename_metadata_20241201_143022.json # Crawl metadata
├── sitename_index_20241201_143022.md      # Content index
└── sections/                              # Individual section files
    ├── getting-started.md
    ├── api-reference.md
    ├── configuration.md
    ├── tutorials.md
    └── advanced.md
```

### File Descriptions

#### 📄 Combined Markdown File (`sitename_docs_*.md`)

- **Purpose**: Single comprehensive file with all documentation
- **Use case**: Perfect for LLM training and context
- **Format**: Structured with table of contents and clear section separators
- **Size**: Typically 1-50MB depending on documentation size

**Example structure:**

```markdown
# Site Documentation

**Source:** https://example.com/docs/
**Generated:** 2024-12-01 14:30:22
**Total Pages:** 47
**Total Words:** 125,432

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Reference](#api-reference)
   ...

# 1. Getting Started

**Path:** `getting-started`
**Description:** Introduction to the platform
**Word Count:** 1,234

[Content here...]

====================================================================================================

# 2. API Reference

...
```

#### 📋 Metadata JSON File (`sitename_metadata_*.json`)

- **Purpose**: Detailed crawl statistics and page information
- **Contents**: URLs, word counts, success rates, failed pages
- **Use case**: Analysis, debugging, and progress tracking

**Example structure:**

```json
{
  "site_info": {
    "name": "example-docs",
    "base_url": "https://example.com/docs/",
    "crawled_at": "2024-12-01T14:30:22",
    "crawler_version": "2.0"
  },
  "crawl_stats": {
    "total_pages": 47,
    "total_words": 125432,
    "success_rate": 94.0,
    "failed_urls": 3
  },
  "pages": [
    {
      "url": "https://example.com/docs/getting-started",
      "title": "Getting Started",
      "word_count": 1234,
      "path": "getting-started"
    }
  ]
}
```

#### 📑 Index Markdown File (`sitename_index_*.md`)

- **Purpose**: Human-readable overview of all content
- **Contents**: Section summaries, page statistics, content organization
- **Use case**: Quick reference and content navigation

#### 📁 Section Files (`sections/*.md`)

- **Purpose**: Individual files organized by documentation sections
- **Organization**: Grouped by URL path structure
- **Use case**: Targeted queries and specific topic analysis

## 🎯 Supported Documentation Sites

The crawler works with most documentation websites, including:

### ✅ Tested Sites

| Site             | URL                             | Pages | Notes               |
| ---------------- | ------------------------------- | ----- | ------------------- |
| **Caddy Server** | https://caddyserver.com/docs/   | ~50   | Excellent structure |
| **FastAPI**      | https://fastapi.tiangolo.com/   | ~80   | Rich content        |
| **Python Docs**  | https://docs.python.org/3/      | ~200+ | Large site          |
| **Kubernetes**   | https://kubernetes.io/docs/     | ~300+ | Complex navigation  |
| **Next.js**      | https://nextjs.org/docs         | ~60   | Modern framework    |
| **React**        | https://react.dev/              | ~40   | Clean structure     |
| **Vue.js**       | https://vuejs.org/guide/        | ~50   | Well organized      |
| **Django**       | https://docs.djangoproject.com/ | ~150+ | Comprehensive       |
| **Express.js**   | https://expressjs.com/          | ~30   | Simple structure    |
| **Tailwind CSS** | https://tailwindcss.com/docs    | ~100+ | Design system       |

### 🔧 Site-Specific Optimizations

The crawler automatically detects and adapts to:

#### **GitBook Sites**

- Detects `.page-inner` content containers
- Handles navigation structure
- Preserves chapter organization

#### **Docusaurus Sites**

- Recognizes `.markdown` content areas
- Filters out sidebar navigation
- Maintains version structure

#### **MkDocs Sites**

- Targets `.md-content` areas
- Handles search integration
- Preserves navigation hierarchy

#### **Sphinx Documentation**

- Identifies `.document` containers
- Filters sidebar content
- Maintains cross-references

#### **Custom Documentation Platforms**

- Adaptive content detection
- Flexible CSS selectors
- Configurable filtering

## 🛠️ Advanced Features

### Smart URL Filtering

The crawler automatically excludes:

#### **Template Variables**

- `${variable}` - Shell-style variables
- `{{placeholder}}` - Handlebars/Mustache templates
- `<placeholder>` - Angle bracket placeholders
- URL-encoded variants (`%7B`, `%7D`)

#### **Authentication & Commerce**

- Login, register, signup pages
- Shopping cart, checkout pages
- User account, profile pages
- Admin, dashboard interfaces

#### **Non-Content Files**

- Binary files (PDF, ZIP, executables)
- Media files (images, videos)
- Archive files (tar, gz)

#### **Navigation Elements**

- Fragment links (URLs with `#` anchors)
- Pagination (URLs with page parameters)
- Search results pages
- Tag/category pages

### Content Cleaning Pipeline

#### **Stage 1: UI Element Removal**

```python
# Removes common UI patterns
ui_patterns = [
    "Skip to content",
    "Navigation menu",
    "Search",
    "Cookie notice",
    "Edit this page",
    "Last updated",
    "Share", "Print"
]
```

#### **Stage 2: Link Processing**

- Convert relative URLs to absolute
- Remove JavaScript links
- Filter anchor-only links
- Preserve meaningful links

#### **Stage 3: Structure Normalization**

- Limit header levels (max 4 for LLM clarity)
- Standardize code block formatting
- Clean table structures
- Normalize whitespace

#### **Stage 4: LLM Optimization**

- Ensure proper spacing around headers
- Maintain code block integrity
- Preserve list structures
- Optimize for token efficiency

### Error Handling & Recovery

#### **Graceful Failure Management**

- Continue crawling despite individual page errors
- Log failed URLs for review
- Provide detailed error context
- Maintain crawl statistics

#### **Timeout Handling**

- Configurable page load timeouts
- Skip pages that take too long
- Prevent crawler from hanging
- Log timeout incidents

#### **Invalid URL Detection**

- Pre-validate URLs before crawling
- Detect template variables
- Skip malformed URLs
- Provide clear skip reasons

#### **Rate Limit Compliance**

- Automatic delays between requests
- Respect server response times
- Configurable crawl speeds
- Monitor for rate limiting

## 📊 Performance & Statistics

### Typical Performance Metrics

| Metric           | Range            | Notes                  |
| ---------------- | ---------------- | ---------------------- |
| **Speed**        | 2-5 pages/second | With respectful delays |
| **Success Rate** | 85-95%           | Well-structured sites  |
| **Memory Usage** | 100-500MB        | Depends on site size   |
| **Word Count**   | 50,000-500,000   | Per documentation site |

### Resource Usage

#### **Disk Space Requirements**

- **Small sites** (5-20 pages): 1-5MB output
- **Medium sites** (20-100 pages): 5-50MB output
- **Large sites** (100+ pages): 50-500MB output
- **Browser cache**: 100-200MB (one-time download)

#### **Network Usage**

- **Bandwidth**: 1-10MB per crawl session
- **Requests**: 1-2 requests per page (plus resources)
- **Rate limiting**: Built-in 1-2 second delays

#### **Processing Time**

- **Small documentation sites**: 1-5 minutes
- **Medium documentation sites**: 5-30 minutes
- **Large documentation sites**: 30-120 minutes

## 🤝 Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/universal-docs-crawler.git
cd universal-docs-crawler

# Install development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/crawl4dev

# Run specific test file
uv run pytest tests/test_crawler.py

# Run with verbose output
uv run pytest -v
```

### Code Quality Checks

```bash
# Type checking
uv run mypy src/

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Check imports
uv run ruff check --select I src/ tests/
```

### Making Changes

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** your changes with proper tests
4. **Run** quality checks: `uv run ruff check && uv run mypy src/`
5. **Test** your changes: `uv run pytest`
6. **Commit** with clear messages: `git commit -m "Add feature description"`
7. **Push** and create a pull request

### Testing Guidelines

- **Unit tests** for individual functions
- **Integration tests** for crawler workflows
- **Mock external requests** in tests
- **Test error conditions** and edge cases
- **Maintain >90% code coverage**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Crawl4AI](https://github.com/unclecode/crawl4ai)** - The powerful crawling engine that makes this possible
- **[Playwright](https://playwright.dev/)** - Modern browser automation
- **[Pydantic](https://pydantic.dev/)** - Data validation and settings management

## 📞 Support

### Getting Help

- **Documentation**: This README contains comprehensive usage instructions
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/universal-docs-crawler/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/universal-docs-crawler/discussions)

### Reporting Issues

When reporting bugs, please include:

1. **Your operating system** (Windows, macOS, Linux)
2. **Python version** (`python --version`)
3. **Installation method** (pipx, uv, pip)
4. **Full error message** (copy and paste from terminal)
5. **The URL you were trying to crawl**
6. **Steps to reproduce** the issue

### Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain why** it would be valuable
4. **Provide examples** if possible

---

**Made with ❤️ for the AI and documentation community**
