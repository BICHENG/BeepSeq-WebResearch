# client.py
import httpx
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

class OutputFormat(str, Enum):
    html = "html"
    text = "text"
    markdown = "markdown"

@dataclass
class CrawlerConfig:
    output_format: OutputFormat = OutputFormat.markdown
    include_comments: bool = True
    include_tables: bool = True
    include_images: bool = True
    include_links: bool = True
    favor_recall: bool = True
    deduplicate: bool = True
    with_metadata: bool = True
    no_cache: bool = False

class WebResearchClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def read(self, url: Optional[str] = None, urls: Optional[List[str]] = None, config: Optional[CrawlerConfig] = None):
        if not url and not urls:
            raise ValueError("Provide URL(s)")
        
        config = config or CrawlerConfig()
        async with httpx.AsyncClient() as client:
            if url:
                response = await client.get(f"{self.base_url}/read", params={"url": url})
            else:
                response = await client.post(f"{self.base_url}/read", json={"urls": urls, "config": config.__dict__})
            response.raise_for_status()
            return response.json()

    async def search(self, query: str, max_results: int = 5, fulltext: bool = False, config: Optional[CrawlerConfig] = None):
        config = config or CrawlerConfig()
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/search", params={
                "query": query,
                "max_results": max_results,
                "fulltext": fulltext,
                **config.__dict__
            })
            response.raise_for_status()
            return response.json()

# Example usage:
# client = WebResearchClient()
# results = asyncio.run(client.search("AI最新进展", max_results=3, fulltext=True))