# core.py
from enum import Enum
import asyncio
import nodriver as uc
import trafilatura
from dataclasses import dataclass
from cachetools import LRUCache
from fastapi import FastAPI, HTTPException, Query, Body
from duckduckgo_search import DDGS
from asyncio import Lock

from alive_progress import alive_bar, config_handler

config_handler.set_global(spinner='dots', bar='smooth')

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

class WebCrawler:
    def __init__(self, max_cache=256):
        self.browser = None
        self.cache = LRUCache(maxsize=max_cache)
        self.lock = Lock()

    async def fetch(self, url, config):
        if not config.no_cache and (cached := self.cache.get(url)):
            return cached
                
        page = await self.browser.get(url, new_tab=True)
        await page.wait()
        await page.bring_to_front()
        await page.scroll_down(1080)
        await page.wait(1)
        await page.scroll_down(1080)
        await page.wait(1)
        content = await page.get_content()
        await page.close()

        result = trafilatura.extract(content, **{
            'output_format': config.output_format.value,
            'include_comments': config.include_comments,
            'include_tables': config.include_tables,
            'include_images': config.include_images,
            'include_links': config.include_links,
            'favor_recall': config.favor_recall,
            'deduplicate': config.deduplicate,
            'with_metadata': config.with_metadata,
            'url': url
        }) or "No content extracted"
        
        self.cache[url] = result
        return result

    async def crawl(self, urls, config):
        results = {}
                
        if not self.browser:
            self.browser = await uc.start()
            await self.browser.get("about:blank")
        
        with alive_bar(len(urls)) as bar:
            async def worker(url):
                try:
                    results[url] = await self.fetch(url, config)
                except Exception as e:
                    results[url] = str(e)
                    raise e
                finally:
                    bar()
                    print(f"📖 Parsed {url}")

            await asyncio.gather(*(worker(url) for url in urls))
        return results

    def search(self, query, max_results=5, use_cache=True):
        cache_query_str = f"search:{query},max_results={max_results}"
        
        if use_cache and (rslt := self.cache.get(cache_query_str)):
            print("🔍 Using cache")
            return rslt
        print("🔍 DDGS")
        rslt = DDGS().text(query, max_results=int(max_results))
        ret = [r['href'] for r in rslt], [r['body'] for r in rslt]
        self.cache[cache_query_str] = ret
        return ret

def create_app():
    app = FastAPI()
    crawler = WebCrawler()

    @app.api_route("/read", methods=["GET", "POST"])
    async def read(
        url: str = Query(None),
        urls: list[str] = Body(None),
        config: CrawlerConfig = CrawlerConfig()
    ):
        urls = [url] if url else (urls or [])
        if not urls:
            raise HTTPException(400, "Provide URL(s)")
            
        results = await crawler.crawl(urls, config)
        return results if len(urls) > 1 else results[urls[0]]

    @app.get("/search")
    async def search(query: str, max_results=5,
                     fulltext=False,
                     with_searched_body=False,
                     config=CrawlerConfig()):
        print(f"🔍 Searching for {query}")
        
        urls, body_contents = crawler.search(query, max_results)
        if not fulltext:
            return {"results": zip(urls, body_contents)}
            
        return {"results": await crawler.crawl(urls, config)}

    return app