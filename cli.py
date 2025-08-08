#!/usr/bin/env python3
"""
cli.py - Command Line Interface for BeepSeq WebResearch tool.
"""
import typer
import uvicorn
import asyncio
from typing import Optional, List
from rich import print
from rich.markdown import Markdown
from core import create_app, CrawlerConfig

app = typer.Typer()

@app.command()
def serve(port: int = 8000):
    """启动FastAPI服务器"""
    print(f"🚀 [bold green]Starting server at http://localhost:{port}[/bold green]")
    uvicorn.run(create_app(), host="0.0.0.0", port=port)

@app.command()
def search(
    query: str,
    max_results: int = typer.Option(3, "--max-results", "-m", help="Maximum number of search results."),
    fulltext: bool = typer.Option(False, "--fulltext", "-f", help="Fetch full text of the search results."),
):
    """使用DuckDuckGo进行搜索，并可选择性提取全文"""
    from core import WebCrawler
    
    async def run_search():
        crawler = WebCrawler()
        try:
            if fulltext:
                config = CrawlerConfig(embed_images=True, save_markdown=True)
                urls, _ = crawler.search(query, max_results)
                results = await crawler.crawl(urls, config)
                for url, content in results.items():
                    print(f"URL: {url}")
                    print(Markdown(content))
            else:
                urls, snippets = crawler.search(query, max_results)
                for url, snippet in zip(urls, snippets):
                    print(f"URL: {url}\nSnippet: {snippet}\n")
        finally:
            await crawler.close()
            
    asyncio.run(run_search())

@app.command()
def read(
    url: str = typer.Argument(..., help="The URL to fetch content from."),
    md: bool = typer.Option(True, "--md/--no-md", help="Save as Markdown."),
    html: bool = typer.Option(False, "--html/--no-html", help="Save as HTML."),
    output_dir: str = typer.Option("output", "--output-dir", "-o", help="Output directory."),
    use_trafilatura: bool = typer.Option(False, "--use-trafilatura", help="Force use of trafilatura extractor."),
    no_embed: bool = typer.Option(False, "--no-embed", help="Disable image embedding."),
):
    """从URL提取内容，嵌入图像，并保存为Markdown或HTML。"""
    from core import WebCrawler

    if not md and not html:
        print("⚠️ [bold yellow]No output format specified. Defaulting to Markdown.[/bold yellow]")
        md = True

    config = CrawlerConfig(
        save_markdown=md,
        save_html=html,
        output_dir=output_dir,
        embed_images=not no_embed,
        use_readability=not use_trafilatura
    )

    async def run_crawl():
        crawler = WebCrawler()
        try:
            await crawler.crawl([url], config)
        finally:
            await crawler.close()

    method = "trafilatura" if use_trafilatura else "readability-lxml"
    print(f"🚀 [bold green]Starting crawl for '{url}' using {method}...[/bold green]")
    asyncio.run(run_crawl())
    print("✅ [bold green]Crawl finished.[/bold green]")


if __name__ == "__main__":
    app()
