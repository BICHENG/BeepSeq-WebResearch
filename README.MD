# BeepSeq-WebResearch

**Extracts clean, RAG-friendly Markdown from any webpage.**

BeepSeq-WebResearch is a powerful web content extraction tool designed to fetch the main text and relevant images from any URL and convert it into a clean, self-contained Markdown file. It intelligently handles complex scenarios like lazy-loading images and bypasses anti-scraping measures by leveraging a real browser environment.

This tool is ideal for developers and researchers building Retrieval-Augmented Generation (RAG) systems, enabling high-quality data pipelines for LLMs.

[![License: WTFPL](https://img.shields.io/badge/License-WTFPL-brightgreen.svg)](http://www.wtfpl.net/about/)

---

## Architecture Overview

The tool is designed with a dual-mode architecture for maximum flexibility:

1.  **Standalone CLI**: For quick, on-demand tasks, you can use the `webresearch` command directly. It spins up a browser instance, performs the extraction, and shuts down, all in a single process.
2.  **Client-Server Mode**: For continuous or programmatic use, you can run `webresearch serve` to launch a persistent FastAPI server. You can then interact with this server via its HTTP API, using the provided Python client or any other HTTP tool.

## Features

-   **RAG-Ready Markdown**: Outputs clean, structured Markdown, perfect for LLM ingestion and RAG pipelines.
-   **Intelligent Content Extraction**: Utilizes a robust engine (`readability-lxml`) to accurately extract the main content while preserving structure.
-   **Embedded Images**: Seamlessly fetches and embeds all relevant images as base64, creating fully self-contained documents.
-   **Robust & Resilient**: Built on `nodriver` to handle dynamic content, lazy-loading, and anti-bot measures effectively.
-   **High-Performance**: Employs asynchronous processing and high-speed parallel image downloads.
-   **Flexible**: Offers a fallback extraction engine (`trafilatura`) for compatibility.
-   **Dual-Mode Interface**: Provides both a standalone command-line interface (CLI) and a FastAPI server for programmatic access.

## Getting Started

### Prerequisites

-   Python 3.9+
-   Google Chrome (or a Chromium-based browser) installed.

### Installation

```bash
pip install git+https://github.com/BICHENG/BeepSeq-WebResearch.git
```

---

## Usage

### Mode 1: Standalone CLI

The CLI is the quickest way to extract content from a URL without running a server.

**Extract and Save as Markdown (with embedded images):**
```bash
webresearch read "https://your-target-url.com"
```
This will create a `.md` file in the `output/` directory.

**Extract and Save as both HTML and Markdown:**
```bash
webresearch read "https://your-target-url.com" --html --md
```

**Search and Extract Full Text from Results:**
```bash
webresearch search "Your search query" --max-results 3 --fulltext
```

### Mode 2: Client-Server

This mode is ideal for integrating the tool into your applications.

**Step 1: Start the server**
```bash
webresearch serve --port 8000
```
The server will now be running in the background.

**Step 2: Use the Python client to make requests**

We provide a simple async client in `client.py`. You can use it as follows:

```python
import asyncio
from webresearch.client import WebResearchClient, CrawlerConfig

async def main():
    client = WebResearchClient(base_url="http://localhost:8000")

    # Example 1: Read a single URL
    try:
        print("--- Reading a single URL ---")
        # Note: The server uses default config unless specified in the request body,
        # which is more complex. For CLI-like control, direct crawl is better.
        # The client library here shows basic GET interaction.
        content = await client.read(url="https://www.bilibili.com/video/BV1c1421f7bK/")
        print(f"Successfully extracted content (first 200 chars):\\n{content[:200]}...")

    except Exception as e:
        print(f"An error occurred: {e}")

    # Example 2: Search for a query
    try:
        print("\\n--- Searching for a query ---")
        results = await client.search(query="NVIDIA Blackwell", max_results=2)
        print(f"Search results: {results}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())

```

### Mode 3: AI Agent / Cursor Integration

For the most powerful workflow, you can expose the server as a set of tools for an AI agent like Cursor.

**Step 1: Start the server**
```bash
webresearch serve --port 8000
```

**Step 2: Configure Cursor's MCP**

Open Cursor's `mcp.json` file. You can find it at:
*   **Windows**: `C:\Users\<YourUsername>\.cursor\mcp.json`
*   **macOS/Linux**: `~/.cursor/mcp.json`

Add a new entry for your local server:

```json
{
  "mcpServers": {
    "...": {
      "...": "..."
    },
    "webresearch": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```
**Note:** Remember to replace `...` with your existing configurations for other servers.

**Step 3: Reload Cursor and Use the Tools**

After reloading Cursor (you can use the `Reload Window` command), you can now use the tools directly in the chat:

**Example 1: Search the web**
```
@webresearch search_web query="Latest AI advancements"
```

**Example 2: Read a specific URL**
```
@webresearch read_url url="https://en.wikipedia.org/wiki/Artificial_intelligence"
```

**Example 3: Batch read (GET) with comma-separated URLs**
```
@webresearch read_url urls="https://example.com,https://en.wikipedia.org/wiki/WTFPL"
```

**Example 4: Batch read (POST) with advanced config**
```
@webresearch read_urls urls=["https://example.com","https://example.org"] config={"embed_images":true,"save_markdown":true}
```

## Showcase

For detailed examples, including comparisons and advanced use-cases, please see our [**Showcase & Examples**](docs/showcase.md) page.

## Roadmap

-   [x] **MCP Server Integration**: Expose the `read` and `search` endpoints as Model Context Protocol (MCP) tools. This will turn the service into a compliant MCP server, allowing AI agents and applications (like Cursor) to discover and use its web research capabilities natively.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project uses the WTFPL v2 (Do What The Fuck You Want To Public License). See the [LICENSE](LICENSE) file for details.
