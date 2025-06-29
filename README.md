# Universal Documentation Crawler

A powerful, intelligent web crawler designed specifically for extracting clean, LLM-optimized markdown from documentation websites. Built with Python and Crawl4AI, this tool automatically discovers, crawls, and processes documentation sites to create structured markdown files perfect for AI training and knowledge base creation.

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

### Prerequisites

- **Python 3.8+**
- **uv** (recommended) or **pip** for package management
- **Internet connection** for crawling
- **~200MB disk space** for browser binaries

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/universal-docs-crawler.git
    cd universal-docs-crawler
    ```

2.  **Set up Python environment (recommended):**

    ```bash
    # Using uv (creates virtual environment automatically)
    uv sync

    # Or using pip with virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Python dependencies:**

    ```bash
    # Using uv (recommended - handles everything automatically)
    uv add crawl4ai pyyaml

    # Or using pip
    pip install crawl4ai pyyaml
    ```

4.  **Install Playwright browsers (REQUIRED):**

    ```bash
    # This downloads the actual browser binaries that Crawl4AI uses
    # Using uv
    uv run playwright install chromium

    # Or using pip
    playwright install chromium

    # Or install all browsers (larger download)
    playwright install
    ```

### Verify Installation

Test that everything is working:

```bash
# Quick test
uv run main.py --create-config

# Test crawling
uv run main.py https://httpbin.org/html --max-pages 1
```

### Basic Usage

```bash
# Crawl a documentation site
uv run main.py https://caddyserver.com/docs/

# Crawl with custom settings
uv run main.py https://fastapi.tiangolo.com/ --max-pages 30 --output-dir fastapi_docs

# Create a sample configuration file
uv run main.py --create-config
```

## 📦 Dependencies Explained

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
| **Memory Usage** | 100              |
