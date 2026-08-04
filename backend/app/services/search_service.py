import httpx
import re
import urllib.parse
from typing import List, Dict, Any
from app.core.config import settings

class SearchService:
    def __init__(self):
        self.tavily_key = settings.TAVILY_API_KEY
        self.serpapi_key = settings.SERPAPI_KEY

    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes web search across configured search APIs (Tavily, SerpAPI) 
        with automatic fallback to DuckDuckGo HTML scraping.
        """
        results = []
        
        # 1. Try Tavily Search API if key provided
        if self.tavily_key:
            try:
                results = await self._search_tavily(query, max_results)
                if results:
                    return results
            except Exception as e:
                print(f"[SearchService] Tavily search error: {e}")

        # 2. Try SerpAPI if key provided
        if self.serpapi_key:
            try:
                results = await self._search_serpapi(query, max_results)
                if results:
                    return results
            except Exception as e:
                print(f"[SearchService] SerpAPI search error: {e}")

        # 3. Fallback: DuckDuckGo / Direct HTTP Search Scraper
        try:
            results = await self._search_ddg_fallback(query, max_results)
        except Exception as e:
            print(f"[SearchService] DDG fallback error: {e}")
            
        return results

    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": max_results,
                    "include_raw_content": True
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                items = []
                for res in data.get("results", []):
                    items.append({
                        "title": res.get("title", query),
                        "url": res.get("url", ""),
                        "snippet": res.get("content", ""),
                        "full_text": res.get("raw_content") or res.get("content", ""),
                        "domain": urllib.parse.urlparse(res.get("url", "")).netloc,
                        "published_date": res.get("published_date", "2026")
                    })
                return items
        return []

    async def _search_serpapi(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": max_results
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                items = []
                for res in data.get("organic_results", []):
                    items.append({
                        "title": res.get("title", ""),
                        "url": res.get("link", ""),
                        "snippet": res.get("snippet", ""),
                        "full_text": res.get("snippet", ""),
                        "domain": urllib.parse.urlparse(res.get("link", "")).netloc,
                        "published_date": res.get("date", "2026")
                    })
                return items
        return []

    async def _search_ddg_fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo HTML parsing"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            resp = await client.get(f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}")
            items = []
            if resp.status_code == 200:
                html = resp.text
                # regex extract links and titles
                link_matches = re.findall(r'<a class="result__url" href="([^"]+)">', html)
                title_matches = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html)
                snippet_matches = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)
                
                for idx in range(min(len(link_matches), max_results)):
                    url = link_matches[idx]
                    # clean DDG redirect URLs if needed
                    if "/l/?" in url:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        if "uddg" in parsed:
                            url = parsed["uddg"][0]
                    
                    title = re.sub('<[^<]+?>', '', title_matches[idx]) if idx < len(title_matches) else query
                    snippet = re.sub('<[^<]+?>', '', snippet_matches[idx]) if idx < len(snippet_matches) else ""
                    
                    items.append({
                        "title": title.strip(),
                        "url": url,
                        "snippet": snippet.strip(),
                        "full_text": snippet.strip(),
                        "domain": urllib.parse.urlparse(url).netloc,
                        "published_date": "2026"
                    })
            return items

    async def fetch_full_text(self, url: str) -> str:
        """Fetches full page content for raw document collection"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EnterpriseResearchAgent/1.0"
        }
        try:
            async with httpx.AsyncClient(timeout=8.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    # Strip tags to get raw clean text
                    text = re.sub(r'<script.*?>.*?</script>', '', resp.text, flags=re.DOTALL)
                    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
                    text = re.sub(r'<[^<]+?>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text[:8000]  # cap length for storage efficiency
        except Exception as e:
            print(f"[SearchService] Failed to scrape {url}: {e}")
        return ""

search_service = SearchService()
