# Universal Documentation Crawler

A powerful, intelligent web crawler designed specifically for extracting clean, LLM-optimized markdown Step 1: Download the code

````bash
git clone https://github.com/Retrockit/universal-docs-crawler.git
cd universal-docs-crawler
```ocumentation websites. Built with Python and Crawl4AI, this tool automatically discovers, crawls, and processes documentation sites to create structured markdown files perfect for AI training and knowledge bases.

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
````

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
pipx install git+https://github.com/Retrockit/universal-docs-crawler.git
```

Step 5: Install required browser files

```bash
# Install playwright in the same environment
pipx inject crawl4dev playwright

# Install browser binaries using the injected playwright
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
uvx --from git+https://github.com/Retrockit/universal-docs-crawler.git crawl4dev https://fastapi.tiangolo.com/

# Option B: Install for repeated use
uvx install git+https://github.com/Retrockit/universal-docs-crawler.git

# Install browser files (required for Option B)
uvx run --from git+https://github.com/Retrockit/universal-docs-crawler.git playwright install chromium

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
git clone https://github.com/Retrockit/universal-docs-crawler.git
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
git clone https://github.com/Retrockit/universal-docs-crawler.git
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
pip install git+https://github.com/Retrockit/universal-docs-crawler.git
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

#### Example 1: Crawl a Small Documentation Site (LLM-Ready)

```bash
crawl4dev https://httpbin.org/html --max-pages 5
```

**What this does:**

- Downloads up to 5 pages from the website
- Saves results in a folder called `crawled_docs/`
- Creates several files with the extracted content
- **Automatically creates LLM-friendly chunks** in `crawled_docs/chunks/`

#### Example 2: Crawl with Custom Settings and LLM Optimization

```bash
crawl4dev https://fastapi.tiangolo.com/ --max-pages 20 --output-dir my_docs --site-name fastapi --chunk-size 4000
```

**What each option means:**

- `--max-pages 20`: Download at most 20 pages
- `--output-dir my_docs`: Save files in a folder called `my_docs/`
- `--site-name fastapi`: Name the output files with "fastapi" prefix
- `--chunk-size 4000`: Create chunks of ~4,000 tokens each (works with most LLMs)

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

| Option                | What it does                        | Example                      |
| --------------------- | ----------------------------------- | ---------------------------- |
| `--max-pages NUMBER`  | Limit how many pages to download    | `--max-pages 50`             |
| `--output-dir FOLDER` | Choose where to save files          | `--output-dir my_folder`     |
| `--site-name NAME`    | Choose a name for output files      | `--site-name my_site`        |
| `--chunk-size NUMBER` | Create LLM-friendly chunks (tokens) | `--chunk-size 4000`          |
| `--no-chunking`       | Disable automatic chunking          | `--no-chunking`              |
| `--config FILE`       | Use settings from a file            | `--config my_config.yaml`    |
| `--create-config`     | Create a sample settings file       | (no additional value needed) |
| `--help`              | Show all available options          | (no additional value needed) |

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

    # Save results to files with chunking enabled
    if results:
        output_files = crawler.save_llm_optimized_results(
            results,
            base_output_dir='my_crawled_docs',
            site_name='python_docs',
            enable_chunking=True,
            chunk_size=6000  # Good size for GPT-4
        )
        combined_file, metadata_file, index_file, sections_dir, chunks_dir = output_files
        print(f"Combined file: {combined_file}")
        if chunks_dir:
            print(f"LLM chunks available in: {chunks_dir}")

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

### Chunking and LLM Integration Issues

#### Problem: Chunks are still too large for my LLM

**Solution:**

```bash
# Use smaller chunk size
crawl4dev https://docs.example.com --chunk-size 3000  # For very small context models

# Check chunk sizes before using
cat crawled_docs/chunks/*_manifest.json | grep word_count
```

#### Problem: Chunks break in the middle of important content

**Solution:**

```yaml
# In crawler_config.yaml - improve semantic splitting
chunk_settings:
  semantic_splitting: true # Split at headers, not arbitrary points
  preserve_code_blocks: true # Keep code examples intact
  min_chunk_size: 1000 # Prevent tiny fragments
```

#### Problem: I want to disable chunking completely

**Solution:**

```bash
# Disable automatic chunking
crawl4dev https://docs.example.com --no-chunking

# Or generate only the traditional combined file
crawl4dev https://docs.example.com --legacy-output
```

#### Problem: Need different chunk sizes for different LLM models

**Solution:**

```bash
# Create multiple chunk sets for different models
crawl4dev https://docs.example.com --chunk-size 4000 --output-dir grok_chunks
crawl4dev https://docs.example.com --chunk-size 15000 --output-dir claude_chunks
crawl4dev https://docs.example.com --chunk-size 4000 --output-dir standard_chunks
```

#### Problem: Want to post-process chunks for specific LLM formats

**Solution:**

```python
# Custom chunk processing for your LLM API
import json
from pathlib import Path

def format_for_my_llm(chunk_dir):
    manifest_path = chunk_dir / 'chunk_manifest.json'
    with open(manifest_path) as f:
        manifest = json.load(f)

    formatted_chunks = []
    for chunk_info in manifest['chunks']:
        chunk_path = chunk_dir / chunk_info['filename']
        with open(chunk_path) as f:
            content = f.read()

        # Format for your specific LLM
        formatted = {
            'role': 'user',
            'content': f"Documentation Context:\n\n{content}",
            'metadata': chunk_info
        }
        formatted_chunks.append(formatted)

    return formatted_chunks

# Usage
chunks = format_for_my_llm(Path('crawled_docs/chunks'))
```
