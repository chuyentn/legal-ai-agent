"""
Legal Document Crawler — Powered by CrawlKit
Crawl Vietnamese legal websites and index documents automatically.
"""
import os
import re
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Supported legal sources
LEGAL_SOURCES = {
    "thuvienphapluat": {
        "name": "Thư Viện Pháp Luật",
        "base_url": "https://thuvienphapluat.vn",
        "discover_urls": [
            "https://thuvienphapluat.vn/page/tim-van-ban.aspx",
        ],
        "description": "Largest Vietnamese legal document database"
    },
    "vbpl": {
        "name": "Văn Bản Pháp Luật (Chính Phủ)",
        "base_url": "https://vbpl.vn",
        "discover_urls": [
            "https://vbpl.vn/pages/portal.aspx",
        ],
        "description": "Official government legal portal"
    },
    "congbao": {
        "name": "Công Báo",
        "base_url": "https://congbao.chinhphu.vn",
        "discover_urls": [
            "https://congbao.chinhphu.vn",
        ],
        "description": "Official Gazette of Vietnam"
    }
}

class LegalCrawler:
    def __init__(self, crawlkit_api_key: str, db_connection=None):
        """Initialize crawler with CrawlKit API key."""
        try:
            from crawlkit import CrawlKit
            self.ck = CrawlKit(api_key=crawlkit_api_key, base_url="https://api.crawlkit.org")
            self.enabled = True
        except ImportError:
            logger.warning("CrawlKit not installed. Run: pip install crawlkit")
            self.enabled = False
            self.ck = None
        except Exception as e:
            logger.error(f"CrawlKit init failed: {e}")
            self.enabled = False
            self.ck = None
        
        self.db = db_connection
    
    def crawl_url(self, url: str) -> Dict:
        """Crawl a single legal document URL."""
        if not self.enabled:
            return {"success": False, "error": "CrawlKit not configured. Get your API key at https://crawlkit.org"}
        
        try:
            result = self.ck.scrape(url, format="text", auto_extract=True)
            return {
                "success": True,
                "content": result.get("content", ""),
                "title": result.get("metadata", {}).get("title", ""),
                "url": url,
                "content_type": result.get("content_type", ""),
                "chars": len(result.get("content", "")),
            }
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "403" in error_msg:
                return {"success": False, "error": "Invalid CrawlKit API key. Get a free key at https://crawlkit.org"}
            if "429" in error_msg:
                return {"success": False, "error": "CrawlKit rate limit reached. Upgrade your plan at https://crawlkit.org/pricing"}
            return {"success": False, "error": f"Crawl failed: {error_msg}"}
    
    def discover_links(self, url: str, max_links: int = 50) -> List[str]:
        """Discover legal document links from a page."""
        if not self.enabled:
            return []
        
        try:
            result = self.ck.discover(url)
            links = result.get("links", [])
            # Filter for legal document URLs
            legal_links = [l for l in links if self._is_legal_url(l)]
            return legal_links[:max_links]
        except Exception as e:
            logger.error(f"Discover failed: {e}")
            return []
    
    def crawl_and_index(self, url: str, company_id: str = None) -> Dict:
        """Crawl a URL and index it into the database."""
        # Step 1: Crawl
        result = self.crawl_url(url)
        if not result["success"]:
            return result
        
        content = result["content"]
        title = result["title"] or self._extract_title(content)
        
        if len(content) < 100:
            return {"success": False, "error": "Content too short to index"}
        
        # Step 2: Chunk content
        chunks = self._chunk_content(content, max_chunk_size=1000)
        
        # Step 3: Create document hash (dedup)
        content_hash = hashlib.md5(content[:5000].encode()).hexdigest()
        
        return {
            "success": True,
            "title": title,
            "url": url,
            "content_length": len(content),
            "chunks": len(chunks),
            "content_hash": content_hash,
            "document": {
                "title": title,
                "content": content,
                "url": url,
                "source": self._detect_source(url),
                "chunks": chunks,
            }
        }
    
    def batch_crawl(self, urls: List[str], company_id: str = None) -> Dict:
        """Crawl multiple URLs."""
        if not self.enabled:
            return {"success": False, "error": "CrawlKit not configured"}
        
        try:
            results = self.ck.batch(urls)
            indexed = 0
            errors = 0
            for item in results.get("data", []):
                if item.get("success"):
                    indexed += 1
                else:
                    errors += 1
            
            return {
                "success": True,
                "total": len(urls),
                "indexed": indexed,
                "errors": errors,
                "results": results.get("data", [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sources(self) -> List[Dict]:
        """Get list of supported legal sources."""
        return [
            {"id": k, **v} for k, v in LEGAL_SOURCES.items()
        ]
    
    def _is_legal_url(self, url: str) -> bool:
        """Check if URL is likely a legal document."""
        legal_patterns = [
            r'van-ban', r'phap-luat', r'nghi-dinh', r'thong-tu',
            r'luat', r'quyet-dinh', r'cong-van', r'nghi-quyet',
            r'bo-luat', r'decree', r'circular', r'law'
        ]
        url_lower = url.lower()
        return any(p in url_lower for p in legal_patterns)
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        lines = content.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                return line
        return "Untitled Document"
    
    def _chunk_content(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """Split content into chunks."""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _detect_source(self, url: str) -> str:
        """Detect source from URL."""
        for source_id, source in LEGAL_SOURCES.items():
            if source["base_url"] in url:
                return source["name"]
        return "Custom Source"
