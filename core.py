#!/usr/bin/env python3
"""
core.py - The core logic for BeepSeq WebResearch tool.
Handles web crawling, content extraction, and image embedding.
"""
from enum import Enum
import asyncio
import nodriver as uc
import trafilatura
from dataclasses import dataclass
from cachetools import LRUCache
from fastapi import FastAPI, HTTPException, Query, Body, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from ddgs.ddgs import DDGS
from asyncio import Lock, Semaphore
import os
import re
import base64
import mimetypes
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, Tuple, List, Optional, Union

from pydantic import BaseModel, Field

import requests
from readability import Document
import markdownify
import html2text
import httpx
import browser_cookie3

from alive_progress import alive_bar, config_handler

config_handler.set_global(spinner='dots', bar='smooth')

class OutputFormat(str, Enum):
    html = "html"
    text = "text"
    markdown = "markdown"

class CrawlerConfig(BaseModel):
    output_format: OutputFormat = Field(default=OutputFormat.markdown, description="Output format: markdown or html")
    include_comments: bool = Field(default=True)
    include_tables: bool = Field(default=True)
    include_images: bool = Field(default=True)
    include_links: bool = Field(default=True)
    favor_recall: bool = Field(default=True)
    deduplicate: bool = Field(default=True)
    with_metadata: bool = Field(default=True)
    no_cache: bool = Field(default=False)
    save_html: bool = Field(default=False)
    save_markdown: bool = Field(default=False)
    output_dir: str = Field(default="output")
    embed_images: bool = Field(default=False, description="Embed images as data: URIs into output")
    use_readability: bool = Field(default=True, description="Use readability-lxml; set false to use trafilatura")

class ReadRequest(BaseModel):
    urls: List[str] = Field(..., description="List of webpage URLs to read")
    config: Optional[CrawlerConfig] = Field(default=None, description="Optional crawler config to override defaults")

class WebCrawler:
    def __init__(self, max_cache=256, max_concurrency=20):
        self.browser = None
        self.config = None  # Will be set during crawl
        self.cache = LRUCache(maxsize=max_cache)
        self.lock = Lock()
        self.semaphore = Semaphore(max_concurrency)

    def _extract_images_from_html(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """从HTML中提取图像信息"""
        img_pattern = r'<img[^>]*>'
        images = []
        
        for img_tag in re.finditer(img_pattern, html_content, re.IGNORECASE):
            tag_content = img_tag.group(0)
            
            src_match = re.search(r'src=["\']([^"\']*)["\']', tag_content, re.IGNORECASE)
            if not src_match or src_match.group(1).startswith('data:image'):
                continue
            
            src = src_match.group(1)
            
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', tag_content, re.IGNORECASE)
            alt = alt_match.group(1) if alt_match else ""
            
            full_url = urljoin(base_url, src)
                
            images.append({
                "src": src,
                "full_url": full_url, 
                "alt": alt,
                "original_tag": tag_content
            })
        
        return images

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        return filename[:200] if len(filename) > 200 else filename

    def _extract_content(self, html_content: str, url: str, use_readability: bool) -> Tuple[str, str, str]:
        """根据配置选择提取器提取内容"""
        try:
            if use_readability:
                doc = Document(html_content)
                title = doc.title()
                clean_html = doc.summary()
                h = html2text.HTML2Text()
                h.body_width = 0
                md_content = h.handle(clean_html)
                return title, clean_html, md_content
            else:
                md_content = trafilatura.extract(html_content, include_links=True, url=url)
                title_match = re.search(r'<title[^>]*>([^<]*)</title>', html_content, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else 'untitled'
                return title, html_content, md_content
        except Exception as e:
            print(f"⚠️ Content extraction failed: {e}")
            title_match = re.search(r'<title[^>]*>([^<]*)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else 'untitled'
            return title, html_content, ""

    async def _download_image(self, client: httpx.AsyncClient, img_info: Dict) -> Tuple[str, str]:
        """使用httpx客户端并行下载单个图像"""
        async with self.semaphore:
            try:
                response = await client.get(img_info['full_url'], timeout=30)
                response.raise_for_status()
                content = await response.aread()
                return img_info['full_url'], base64.b64encode(content).decode('utf-8')
            except Exception:
                pass
        return img_info['full_url'], None
    
    def _get_mime_type(self, image_url: str) -> str:
        """根据URL推断MIME类型，提供默认值"""
        ext = os.path.splitext(urlparse(image_url).path)[1].lower()
        return mimetypes.types_map.get(ext, 'application/octet-stream')

    def _replace_image_src(self, content: str, img_info: Dict, data_uri: str) -> str:
        """在HTML或Markdown内容中替换图像src为data URI"""
        return content.replace(img_info['src'], data_uri).replace(img_info['full_url'], data_uri)

    async def fetch(self, url: str, config: CrawlerConfig):
        """核心抓取与处理方法"""
        if not config.no_cache and (cached := self.cache.get(url)):
            return cached
        
        page = None
        try:
            page = await self.browser.get(url, new_tab=True)
            await page.wait()
            await page.scroll_down(1080); await page.wait(1)
            await page.scroll_down(1080); await page.wait(1)
            
            original_html = await page.get_content()
            user_agent = await page.evaluate('navigator.userAgent')

            title, clean_html, md_content = self._extract_content(original_html, url, config.use_readability)

            if config.embed_images:
                images_info = self._extract_images_from_html(clean_html, url)
                if images_info:
                    cookie_file_path = Path(self.browser.config.user_data_dir) / "Default" / "Cookies"
                    
                    try:
                        cj = browser_cookie3.chrome(cookie_file=str(cookie_file_path))
                    except Exception:
                        cj = None

                    headers = {'User-Agent': user_agent, 'Referer': url}
                    async with httpx.AsyncClient(headers=headers, cookies=cj, http2=True, verify=False) as client:
                        tasks = [self._download_image(client, img) for img in images_info]
                        results = await asyncio.gather(*tasks)
                        
                        image_map = {url: data for url, data in results if data}
                        
                        for img_info in images_info:
                            if base64_data := image_map.get(img_info['full_url']):
                                mime_type = self._get_mime_type(img_info['full_url'])
                                data_uri = f"data:{mime_type};base64,{base64_data}"
                                clean_html = self._replace_image_src(clean_html, img_info, data_uri)
                                md_content = self._replace_image_src(md_content, img_info, data_uri)
                        print(f"📊 图像嵌入统计: {len(image_map)}/{len(images_info)} 成功")

            if config.save_html or config.save_markdown:
                safe_title = self._sanitize_filename(title)
                output_path = Path(config.output_dir)
                output_path.mkdir(exist_ok=True)
                
                if config.save_html:
                    html_file = output_path / f"{safe_title}.html"
                    html_file.write_text(clean_html, encoding='utf-8')
                    print(f"💾 HTML saved: {html_file}")
                if config.save_markdown:
                    md_file = output_path / f"{safe_title}.md"
                    md_file.write_text(md_content, encoding='utf-8')
                    print(f"📝 Markdown saved: {md_file}")

            final_content = md_content if config.output_format == OutputFormat.markdown else clean_html
            self.cache[url] = final_content
            return final_content
        finally:
            if page:
                await page.close()

    async def crawl(self, urls: List[str], config: CrawlerConfig):
        """并行处理多个URL"""
        results = {}
        async with self.lock:
            if not self.browser:
                # uc.start() returns a tuple (browser, config)
                self.browser = await uc.start()
        
        async def worker(url):
            try:
                results[url] = await self.fetch(url, config)
            except Exception as e:
                results[url] = f"Error: {e}"
                print(f"❌ Error processing {url}: {e}")
            finally:
                bar()
                print(f"📖 Parsed {url}")

        with alive_bar(len(urls)) as bar:
            await asyncio.gather(*(worker(url) for url in urls))
        return results

    async def close(self):
        """关闭浏览器实例"""
        async with self.lock:
            if self.browser:
                try:
                    await self.browser.stop()
                except Exception as e:
                    print(f"⚠️ Error closing browser: {e}")
                finally:
                    self.browser = None
    
    def search(self, query, max_results=5):
        """使用DDGS进行搜索"""
        return [(r['href'], r['body']) for r in DDGS().text(query, max_results=max_results)]

def create_app():
    """创建FastAPI应用"""
    app = FastAPI(
        title="BeepSeq-WebResearch",
        description="A powerful web research tool for crawling and extracting content from websites, with MCP support.",
        version="1.0.0",
    )
    crawler = WebCrawler()

    # CORS to maximize consumption flexibility (agents, tools, browsers)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("shutdown")
    async def shutdown_event():
        await crawler.close()

    @app.get(
        "/read",
        operation_id="read_url",
        tags=["webresearch", "mcp"],
        summary="Read webpage(s) to clean Markdown",
    )
    async def read_get(
        url: str = Query(None, description="The URL of the webpage to read and extract content from."), 
        urls: Optional[str] = Query(None, description="Comma-separated list of URLs to read in one call"),
        config: CrawlerConfig = Depends()
    ):
        """
        Read Get

        Fetches and extracts the main content of a given webpage URL and returns clean Markdown ready for RAG ingestion.
        Perfect for quickly summarizing articles, docs, or long posts.
        """
        if not url and not urls:
            raise HTTPException(status_code=400, detail="Either 'url' or 'urls' must be provided")
        target_urls = []
        if url:
            target_urls.append(url)
        if urls:
            target_urls.extend([u.strip() for u in urls.split(',') if u.strip()])
        results = await crawler.crawl(target_urls, config)
        return results[target_urls[0]] if len(target_urls) == 1 else results

    @app.post(
        "/read",
        operation_id="read_urls",
        tags=["webresearch", "mcp"],
        summary="Batch read webpages to Markdown",
    )
    async def read_post(body: ReadRequest):
        """
        Read Post

        Fetches and extracts the main content from multiple webpages in parallel.
        Returns a mapping from URL to Markdown, ideal for batch curation and dataset building.
        """
        urls = body.urls
        if not urls:
            raise HTTPException(status_code=400, detail="No URLs provided.")
        config = body.config or CrawlerConfig()
        return await crawler.crawl(urls, config)

    @app.get(
        "/search",
        operation_id="search_web",
        tags=["webresearch", "mcp"],
        summary="Search the web (optionally read fulltext)",
    )
    async def search(
        query: str = Query(..., description="The search query to look up."), 
        max_results: int = Query(3, description="The maximum number of search results to return."), 
        fulltext: bool = Query(False, description="Whether to fetch the full text of the search results."), 
        config: CrawlerConfig = Depends()
    ):
        """
        Search Web

        Finds relevant pages via DuckDuckGo. Return snippets by default, or set fulltext=true to read and return Markdown for each result automatically.
        Great for "search-then-read" workflows.
        """
        urls_snippets = crawler.search(query, max_results)
        if not fulltext:
            return {"results": [{"url": u, "snippet": s} for u, s in urls_snippets]}
        urls_to_crawl = [u for u, _ in urls_snippets]
        return await crawler.crawl(urls_to_crawl, config)

    # 创建并挂载 MCP
    mcp = FastApiMCP(app, name="WebResearch MCP")
    mcp.mount()

    return app

