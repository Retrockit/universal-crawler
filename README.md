# Universal Documentation Crawler 🕷️

**A simple, friendly tool for turning websites into AI-ready text files**

Perfect for folks who want to feed documentation websites to ChatGPT, Claude, or other AI tools! This crawler automatically finds and downloads website content, cleans it up, and saves it in a format that's easy for AI to understand.

## ✨ What Does This Tool Do?

**In simple terms:** Give it a website URL, and it will:

1. 🔍 **Find** all the documentation pages on that website
2. 📄 **Download** the content from each page
3. 🧹 **Clean up** the text (removes menus, ads, and other clutter)
4. 💾 **Save** everything as neat markdown files you can use with AI

**Perfect for:**

- 🤖 Feeding documentation to ChatGPT for questions
- 📚 Creating knowledge bases for AI assistants
- 🎓 Learning new technologies with AI help
- 🔬 Training custom AI models on specific documentation

---

## 🎯 Key Features (What Makes This Special)

### 🧠 **Smart and Simple by Default**

- **No overwhelming options** - Just give it a URL and go!
- **Clean, readable output** - Only creates what you actually need
- **Works out of the box** - Automatically figures out what to crawl
- **Auto-setup** - Browser components install automatically on first use

### 🎨 **Perfect for AI**

- **Removes clutter** - No navigation menus or ads, just pure content
- **Proper formatting** - Clean markdown that AI tools love
- **Right-sized files** - Files are easy to copy-paste into AI chats

### 🛡️ **Respectful and Reliable**

- **Won't break websites** - Crawls slowly and politely
- **Handles errors gracefully** - Keeps going even if some pages fail
- **Shows clear progress** - You always know what's happening

---

## 🚀 Step-by-Step Installation Guide

**This guide is designed to be beginner-friendly and works for all operating systems. Follow each step carefully and in order.**

### Step 1: Make Sure You Have Python

**What is Python?** Python is the programming language this tool is built with. Most computers don't have it installed by default.

**Let's check if you have it:**

1. Open your terminal or command prompt:

   - **Windows**: Press Windows key + R, type `cmd`, press Enter
   - **Mac**: Press Cmd + Space, type `terminal`, press Enter
   - **Linux**: Press Ctrl + Alt + T

2. Type this exact command and press Enter:

```bash
python --version
```

3. Look at what appears on your screen:

   - **If you see "Python 3.11" or higher**: ✅ You're ready! Go to Step 2.
   - **If you see "Python 3.10" or lower**: ❌ You need a newer version.
   - **If you see an error or "command not found"**: ❌ You need to install Python.

4. **For Mac and Linux users**: Also try this command:

```bash
python3 --version
```

If this shows "Python 3.11" or higher, you're good to go! Just remember to use `python3` instead of `python` in future commands.

### Step 1.5: Install Python (Skip This If Step 1 Worked)

#### For Windows Users

1. Go to the official Python website: `https://python.org/downloads/`
2. Click the big yellow "Download Python 3.12" button (or whatever the latest version is)
3. Find the downloaded file (usually in your Downloads folder)
4. Double-click the file to start installation
5. **IMPORTANT**: Check the box that says "Add Python to PATH" ✅
6. Click "Install Now" and wait for it to finish
7. Close your command prompt and open a new one
8. Test it worked: type `python --version`

#### For Mac Users

1. Go to the official Python website: `https://python.org/downloads/`
2. Click "Download Python 3.12" (or latest version)
3. Find the downloaded `.pkg` file in your Downloads folder
4. Double-click it and follow the installation steps
5. Enter your Mac password when asked
6. Open a new Terminal window
7. Test it worked: type `python3 --version`

#### For Linux Users

**Ubuntu or Debian:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora or CentOS:**

```bash
sudo dnf install python3 python3-pip
```

**Arch Linux:**

```bash
sudo pacman -S python python-pip
```

Test it worked: `python3 --version`

### Step 2: Install Git (For Downloading the Project)

**What is Git?** Git is a tool for downloading and managing code projects.

**Check if you have Git:**

```bash
git --version
```

If you see a version number, skip to Step 3. Otherwise, install Git:

#### Install Git on Windows

1. Go to: `https://git-scm.com/download/win`
2. Download "64-bit Git for Windows Setup"
3. Run the downloaded file
4. Keep clicking "Next" with the default settings
5. Click "Install"
6. Close and reopen your command prompt
7. Test: `git --version`

#### Install Git on Mac

**If you have Homebrew:**

```bash
brew install git
```

**If you don't have Homebrew:**

1. Go to: `https://git-scm.com/download/mac`
2. Download and run the installer
3. Follow the installation steps
4. Test: `git --version`

#### Install Git on Linux

**Ubuntu/Debian:**

```bash
sudo apt install git
```

**Fedora/CentOS:**

```bash
sudo dnf install git
```

**Arch Linux:**

```bash
sudo pacman -S git
```

Test: `git --version`

### Step 3: Download the Crawler Project

1. **Create a folder for your projects** (you can skip this if you already have one):

```bash
cd ~
mkdir projects
cd projects
```

2. **Download the crawler code**:

```bash
git clone https://github.com/Retrockit/universal-crawler.git
```

3. **Go into the project folder**:

```bash
cd universal-crawler
```

### Step 4: Install the Crawler Tool

**We'll use the easiest method that works for most people:**

1. **Install pipx** (a tool that makes Python programs easier to manage):

```bash
python -m pip install --user pipx
```

_Note: On Mac/Linux, use `python3` if `python` doesn't work_

2. **Set up pipx properly**:

```bash
python -m pipx ensurepath
```

3. **Close your terminal completely and open a new one** (this is important!)

4. **Install the crawler**:

```bash
pipx install .
```

**That's it!** The crawler is now installed and ready to use. The browser components (needed for crawling modern websites) will be installed automatically the first time you run the crawler.

### Step 5: Test That Everything Works

**Run this command:**

```bash
crawl4dev --help
```

**What should happen:** You should see a help message with lots of options and instructions.

**If you see an error:** Go back and check each step above carefully.

**Note:** If you run `crawl4dev` without any arguments, you'll get an error message. This is normal! The tool needs a website URL to work. Always use `crawl4dev --help` to see the proper usage, or jump straight to Step 6 to try a real example.

### Step 6: Try Your First Crawl! 🎉

**Let's test with a simple website:**

```bash
crawl4dev https://httpbin.org/html --max-pages 1
```

**What will happen:**

1. **First-time setup** (only happens once):

   - The crawler will automatically download and install browser components (Chromium)
   - This takes 2-5 minutes depending on your internet speed
   - You'll see messages like "🎭 First-time setup: Installing Playwright browser..."

2. **Normal crawling**:
   - The crawler will start up and show you progress messages
   - It will download one web page and clean up the content
   - It will create a folder with the results
   - You'll see a success message when it's done

**If this works, you're all set!** You can now crawl any documentation website. Future runs will be much faster since the browser setup only happens once.

---

## 📖 How to Use It

**Important:** The crawler always needs a website URL to work. Never run `crawl4dev` by itself - always provide a website address.

### 🌟 **Simple Mode (Recommended for Beginners)**

**Basic command format:**

```bash
crawl4dev [WEBSITE_URL]
```

**Example - just give it a website and let it work:**

```bash
crawl4dev https://docs.fastapi.tiangolo.com/
```

**What happens:**

- ✅ Creates a folder with the website name (like `fastapi/`)
- ✅ Saves individual markdown files for each page
- ✅ Creates a metadata file with information about what was crawled
- ❌ No extra files or complexity

**Perfect for:** Copy-pasting individual pages into ChatGPT or Claude

### 🎛️ **Advanced Mode (More Features)**

**Want more options? Add some flags:**

```bash
# Get more pages
crawl4dev https://docs.fastapi.tiangolo.com/ --max-pages 50

# Choose where to save files
crawl4dev https://docs.fastapi.tiangolo.com/ --output-dir my_docs

# Create AI-friendly chunks (for training or large documents)
crawl4dev https://docs.fastapi.tiangolo.com/ --enable-chunking

# Get all the extras (combined files, indexes, HTML backup)
crawl4dev https://docs.fastapi.tiangolo.com/ --enable-combined --enable-index --enable-html
```

---

## 🧰 All Available Options

### **Basic Options**

| Option                   | What it does                                            | Example             |
| ------------------------ | ------------------------------------------------------- | ------------------- |
| `--max-pages 20`         | Only crawl 20 pages (instead of default 50)             | Faster crawling     |
| `--output-dir my_folder` | Save files in `my_folder/` instead of auto-naming       | Better organization |
| `--site-name mysite`     | Name your files with "mysite" instead of auto-detecting | Custom naming       |

### **AI-Focused Options** 🤖

| Option              | What it does                          | When to use                           |
| ------------------- | ------------------------------------- | ------------------------------------- |
| `--enable-chunking` | Split content into AI-friendly chunks | For training models or very long docs |
| `--chunk-size 4000` | Make chunks about 4000 tokens each    | To fit your AI model's limits         |

### **Extra Output Options** 📁

| Option              | What it does                         | When to use                           |
| ------------------- | ------------------------------------ | ------------------------------------- |
| `--enable-combined` | Create one big file with all content | When you want everything in one place |
| `--enable-index`    | Create a table of contents file      | To see what's available at a glance   |
| `--enable-sections` | Group content by topic               | To find specific subjects easily      |
| `--enable-html`     | Keep original HTML files too         | For debugging or backup               |

### **Backward Compatibility** 🔄

| Option          | What it does                         | Note                                 |
| --------------- | ------------------------------------ | ------------------------------------ |
| `--no-html`     | Don't save HTML files                | HTML is already off by default       |
| `--no-markdown` | Don't save individual markdown files | Use if you only want combined output |
| `--html-only`   | Only save HTML, skip markdown        | For special use cases                |

---

## 📁 Understanding Your Results

### **Default Output (Simple Mode)**

When you run the tool normally, you get:

```
your_website_name/
├── metadata_20250701_123456.json     # Information about the crawl
└── markdown/                         # Individual page files
    ├── 001_Getting_Started.md
    ├── 002_Installation.md
    └── 003_User_Guide.md
```

**How to use these files:**

- 📋 **Metadata file** - Shows statistics and what was crawled
- 📄 **Markdown files** - Copy these into ChatGPT, Claude, or other AI tools

### **With Optional Features Enabled**

If you use `--enable-chunking --enable-combined --enable-index`:

```
your_website_name/
├── metadata_20250701_123456.json           # Crawl information
├── docs_combined_20250701_123456.md        # Everything in one file
├── index_20250701_123456.md               # Table of contents
├── markdown/                              # Individual pages
├── chunks/                                # AI-friendly chunks
│   ├── chunk_01_getting_started.md
│   ├── chunk_02_installation.md
│   └── chunk_manifest.json               # Chunk information
└── sections/                              # Grouped by topic
    ├── getting_started.md
    └── advanced_usage.md
```

---

## 💡 Real-World Examples

### **Example 1: Quick Documentation Q&A**

```bash
# Download FastAPI docs
crawl4dev https://fastapi.tiangolo.com/

# Copy any .md file from the markdown/ folder into ChatGPT
# Ask: "Based on this FastAPI documentation, how do I create a simple API?"
```

### **Example 2: Learning a New Framework**

```bash
# Get comprehensive docs with sections
crawl4dev https://docs.svelte.dev/ --enable-sections --enable-index

# Use the index.md to see what's available
# Use section files to focus on specific topics
```

### **Example 3: Training Data Preparation**

```bash
# Create AI training chunks
crawl4dev https://docs.python.org/3/ --enable-chunking --chunk-size 4000 --max-pages 100

# Use the chunks/ folder for training or fine-tuning
```

---

## 🐛 Troubleshooting Common Problems

**Don't worry if something goes wrong! Here are solutions to the most common issues.**

### "URL is required" error when running crawl4dev

**If you see something like:**

```
❌ Error: URL is required
Usage: python main.py <URL>
Example: python main.py https://caddyserver.com/docs/
```

**This means:** You ran `crawl4dev` without telling it what website to crawl.

**Solution:** Always provide a website URL:

```bash
# Correct way - provide a URL:
crawl4dev https://docs.fastapi.tiangolo.com/

# To see all options:
crawl4dev --help

# Quick test:
crawl4dev https://httpbin.org/html --max-pages 1
```

### "Command not found" - crawl4dev doesn't work

**This usually means the installation didn't complete properly.**

**Try these solutions in order:**

1. **Make sure you closed and reopened your terminal after installation**

   - Close your terminal/command prompt completely
   - Open a new one
   - Try `crawl4dev --help` again

2. **Check if pipx is working:**

   ```bash
   pipx --version
   ```

   If this gives an error, go back to Step 4 of the installation.

3. **Try the longer command:**

   ```bash
   python -m crawl4dev --help
   ```

   (Use `python3` on Mac/Linux if needed)

4. **Reinstall the crawler:**
   ```bash
   cd ~/projects/universal-crawler
   pipx install --force .
   ```

### "Browser not found" or "Playwright" errors

**This error is very rare now, as the crawler automatically installs browser components on first use.**

**If you still see this error, the automatic installation may have failed.**

**Solution:**

```bash
# Install browser files manually
playwright install chromium

# If that doesn't work, try:
python -m playwright install chromium

# If playwright command is not found, try:
python -m pip install playwright
python -m playwright install chromium
```

**Note:** The crawler should handle this automatically, so if you're seeing this error frequently, please report it as a bug.

### "Permission denied" errors

**This happens when your user account doesn't have the right permissions.**

**On Windows:**

- Right-click your command prompt and choose "Run as administrator"
- Try the installation again

**On Mac/Linux:**

- Make sure you're not using `sudo` with pipx commands
- If you need to, run: `pipx ensurepath` again

### "Module not found" errors

**This means some part of the installation is missing.**

**Solution:**

```bash
# Go back to the project folder
cd ~/projects/universal-crawler

# Force reinstall everything
pipx uninstall crawl4dev
pipx install .
```

### The crawler runs but finds no pages

**Check these things:**

1. **Make sure the website URL is correct:**

   - Try visiting the URL in your web browser first
   - Make sure it actually exists and loads

2. **Try adding common documentation paths:**

   ```bash
   # Instead of: crawl4dev https://example.com
   # Try: crawl4dev https://example.com/docs/
   # Or: crawl4dev https://example.com/documentation/
   ```

3. **Test with a known working site:**
   ```bash
   crawl4dev https://httpbin.org/html --max-pages 1
   ```

### Files are created but they're empty or very short

**This usually means the website is blocking automated crawling.**

**Try these solutions:**

1. **Test with a different website to make sure the tool works**
2. **Try running without headless mode to see what's happening:**

   ```bash
   crawl4dev https://your-site.com --headless false
   ```

   This will show you the browser window so you can see what's happening.

3. **Some websites require you to be logged in or have anti-bot protection**

### The tool is very slow or keeps timing out

**This is normal for large websites, but you can speed it up:**

1. **Limit the number of pages:**

   ```bash
   crawl4dev https://docs.example.com --max-pages 10
   ```

2. **Increase the timeout for slow websites:**
   ```bash
   crawl4dev https://docs.example.com --page-timeout 60000
   ```

### Python version problems

**If you're told your Python is too old:**

1. **Check what version you have:**

   ```bash
   python --version
   python3 --version
   ```

2. **You need Python 3.11 or higher**
3. **Go back to Step 1.5 and install a newer Python version**
4. **On Linux, you might need to install from source or use a newer repository**

### Still having problems?

**Try this step-by-step diagnosis:**

1. **Test Python:**

   ```bash
   python --version
   ```

   Should show 3.11 or higher.

2. **Test pipx:**

   ```bash
   pipx --version
   ```

   Should show a version number.

3. **Test browser installation:**

   ```bash
   playwright install chromium
   ```

   Should download browser files if they're missing.

4. **Test the crawler directly:**

   ```bash
   python -m crawl4dev --help
   ```

   Should show help text.

5. **Test a simple crawl:**
   ```bash
   python -m crawl4dev https://httpbin.org/html --max-pages 1
   ```
   Should successfully crawl one page.

**If any of these steps fail, that's where the problem is. Go back to the installation instructions for that step.**

---

## 🤝 For Developers

### **Using in Python Code**

```python
import asyncio
from crawl4dev import UniversalDocsCrawler

async def crawl_docs():
    crawler = UniversalDocsCrawler()

    # Simple crawl
    results = await crawler.deep_crawl('https://docs.fastapi.tiangolo.com/', max_pages=20)

    # Save with default settings (just markdown + metadata)
    crawler.save_llm_optimized_results(results, 'output_folder')

    # Or save with all features enabled
    crawler.save_llm_optimized_results(
        results,
        'output_folder',
        enable_chunking=True,
        enable_combined=True,
        enable_index=True,
        enable_sections=True,
        save_html=True
    )

# Run it
asyncio.run(crawl_docs())
```

### **Configuration Files**

**Want to save your preferred settings? You can create a configuration file:**

```bash
# Create a sample config
crawl4dev --create-config

# This creates crawler_config.yaml in your current folder
# Edit it to customize your preferred settings

# Then use it:
crawl4dev https://your-site.com --config crawler_config.yaml
```

**The config file includes settings for:**

- How many pages to crawl
- Content extraction rules
- URL patterns to include/exclude
- Output formatting options
- Chunk size settings for AI optimization

---

## 🎯 What's New (Recent Changes)

### **🚀 Automatic Setup (v2.0)**

- **Browser Auto-Install:** First-time users no longer need to manually install Playwright
- **One-Command Setup:** Just `pipx install .` and you're ready to go
- **Smart Error Messages:** Clear, helpful messages when something goes wrong
- **Better Progress Display:** See exactly what's happening during setup and crawling

### **✨ Simplified Default Behavior**

- **Clean Defaults:** Only creates markdown files + metadata by default
- **AI-Optimized Output:** Files are perfectly formatted for AI tools
- **Less Clutter:** No overwhelming file creation unless you specifically ask for it
- **Faster Start:** Get useful results immediately without complex configuration

### **🎛️ Optional Advanced Features**

- **Opt-in Complexity:** Use `--enable-chunking`, `--enable-combined`, etc. for advanced features
- **Smart Chunking:** Better content splitting for AI training and large document processing
- **Flexible Output:** Choose exactly what file types you want
- **Robust Error Handling:** Crawler continues even when individual pages fail
- **Before:** Everything was created by default
- **Why:** You only get what you actually want

### **🤖 Better AI Integration**

- **Now:** Content is optimized specifically for AI tools
- **Before:** Generic markdown output
- **Why:** Works better with ChatGPT, Claude, and other AI systems

---

## 📞 Getting Help

### **Something not working?**

1. 🔍 Check the troubleshooting section above
2. 🧪 Try with a simple, known-working site first
3. 📋 Run with `--help` to see all options
4. � If you find a bug, please report it!

### **Want to contribute?**

- 🌟 Star the repository if it helps you!
- 🐛 Report bugs or suggest improvements
- 📝 Help improve this documentation
- 💻 Submit code improvements

---

## ⚖️ Important Notes

### **Legal and Ethical Use**

- ✅ **Respect robots.txt** - The tool honors website crawling rules
- ✅ **Check terms of service** - Make sure you're allowed to crawl the site
- ✅ **Use responsibly** - Don't overload servers with too many requests
- ✅ **Respect copyright** - Downloaded content may be copyrighted

### **Technical Notes**

- 🐧 **Cross-platform** - Works on Windows, Mac, and Linux
- 🐍 **Python 3.11+** - Requires modern Python
- 🌐 **Browser-based** - Uses Playwright for JavaScript-heavy sites
- 💾 **Local storage** - All files saved to your computer

---

**Happy crawling! 🕷️✨**

_Made with ❤️ for the AI community_
