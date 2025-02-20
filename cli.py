# cli.py
import typer
import uvicorn
import httpx
import asyncio
from typing import Optional, List
from rich import print
from rich.markdown import Markdown
from core import create_app, CrawlerConfig

app = typer.Typer()

# 启动服务端
@app.command()
def serve(port: int = 8000):
    """Start the web research server."""
    uvicorn.run(create_app(), host="0.0.0.0", port=port)

# 搜索并获取结果
@app.command()
def search(
    query: str,
    max_results: int = typer.Option(3, "--max-results", "-m", help="Maximum number of search results."),
    fulltext: bool = typer.Option(False, "--fulltext", "-f", help="Fetch full text of the search results."),
    server_url: str = typer.Option("http://localhost:8000", "--server-url", "-s", help="URL of the running server.")
):
    """Search the web and optionally fetch full text from the server."""
    

    async def fetch_search_results():
        async with httpx.AsyncClient() as client:
            # 发送搜索请求
            search_response = await client.get(
                f"{server_url}/search",
                params={
                    "query": query,
                    "max_results": max_results,
                    "fulltext": fulltext,
                },
                timeout=120
            )
            search_response.raise_for_status()
            return search_response.json()

    # 异步获取结果
    results = asyncio.run(fetch_search_results())

    # 打印结果
    if fulltext:
        for url, content in results["results"].items():
            print(f"## {url}")
            print(Markdown(content))
    else:
        for url, body in results["results"]:
            print(f"## {url}")
            print(Markdown(body))

# 读取指定 URL 的内容
@app.command()
def read(
    url: str = typer.Argument(..., help="The URL to fetch content from."),
    server_url: str = typer.Option("http://localhost:8000", "--server-url", "-s", help="URL of the running server.")
):
    """Fetch and display content from a specific URL."""
    async def fetch_url_content():
        async with httpx.AsyncClient() as client:
            # 发送读取请求
            read_response = await client.get(
                f"{server_url}/read",
                params={"url": url},timeout=120
            )
            read_response.raise_for_status()
            return read_response.json()

    # 异步获取结果
    content = asyncio.run(fetch_url_content())

    # 打印结果
    print(f"## {url}")
    print(Markdown(content))
    
if __name__ == "__main__":
    app()