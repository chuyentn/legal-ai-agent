"""
Crawl Vietnamese law documents from thuvienphapluat.vn.
Phase 1: Bộ luật Lao động 2019 + supporting decrees.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data" / "laws"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Priority law documents to crawl
PRIORITY_LAWS = [
    {
        "name": "Bộ luật Lao động 2019",
        "number": "45/2019/QH14",
        "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Bo-Luat-lao-dong-2019-333670.aspx",
        "type": "bo_luat",
        "domains": ["lao_dong"],
        "issuer": "Quốc hội",
    },
    {
        "name": "Nghị định 145/2020/NĐ-CP",
        "number": "145/2020/NĐ-CP",
        "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-145-2020-ND-CP-huong-dan-Bo-luat-Lao-dong-ve-dieu-kien-lao-dong-460547.aspx",
        "type": "nghi_dinh",
        "domains": ["lao_dong"],
        "issuer": "Chính phủ",
    },
    {
        "name": "Luật Bảo hiểm xã hội 2024",
        "number": "41/2024/QH15",
        "url": "https://thuvienphapluat.vn/van-ban/Bao-hiem/Luat-Bao-hiem-xa-hoi-2024-574592.aspx",
        "type": "luat",
        "domains": ["bhxh", "lao_dong"],
        "issuer": "Quốc hội",
    },
    {
        "name": "Luật An toàn vệ sinh lao động 2015",
        "number": "84/2015/QH13",
        "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Luat-an-toan-ve-sinh-lao-dong-2015-282374.aspx",
        "type": "luat",
        "domains": ["atvs_ld", "lao_dong"],
        "issuer": "Quốc hội",
    },
    {
        "name": "Luật Doanh nghiệp 2020",
        "number": "59/2020/QH14",
        "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Luat-Doanh-nghiep-2020-362817.aspx",
        "type": "luat",
        "domains": ["doanh_nghiep"],
        "issuer": "Quốc hội",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


def crawl_law_page(url: str) -> dict:
    """Crawl a single law document page."""
    print(f"  Crawling: {url[:80]}...")
    
    response = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "lxml")
    
    # Extract main content
    content_div = soup.find("div", class_="content1") or soup.find("div", class_="toanvancontent")
    
    if not content_div:
        # Try alternative selectors
        content_div = soup.find("div", {"id": "toanvancontent"})
    
    text = ""
    if content_div:
        # Clean up the text
        for br in content_div.find_all("br"):
            br.replace_with("\n")
        text = content_div.get_text(separator="\n", strip=True)
    
    return {
        "url": url,
        "html": str(content_div) if content_div else "",
        "text": text,
        "title": soup.title.string if soup.title else "",
    }


def parse_articles(text: str) -> list[dict]:
    """Parse law text into individual articles."""
    articles = []
    current_chapter = ""
    current_section = ""
    current_article = ""
    current_title = ""
    current_content = []
    
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect chapter
        chapter_match = re.match(r"^(Chương\s+[IVXLCDM]+|CHƯƠNG\s+[IVXLCDM]+)", line, re.IGNORECASE)
        if chapter_match:
            # Save previous article
            if current_article and current_content:
                articles.append({
                    "chapter": current_chapter,
                    "section": current_section,
                    "article": current_article,
                    "title": current_title,
                    "content": "\n".join(current_content),
                })
                current_content = []
            current_chapter = line
            continue
        
        # Detect section (Mục)
        section_match = re.match(r"^(Mục\s+\d+)", line, re.IGNORECASE)
        if section_match:
            if current_article and current_content:
                articles.append({
                    "chapter": current_chapter,
                    "section": current_section,
                    "article": current_article,
                    "title": current_title,
                    "content": "\n".join(current_content),
                })
                current_content = []
            current_section = line
            continue
        
        # Detect article (Điều)
        article_match = re.match(r"^(Điều\s+\d+[a-z]?)\.\s*(.*)", line)
        if article_match:
            # Save previous article
            if current_article and current_content:
                articles.append({
                    "chapter": current_chapter,
                    "section": current_section,
                    "article": current_article,
                    "title": current_title,
                    "content": "\n".join(current_content),
                })
            
            current_article = article_match.group(1)
            current_title = article_match.group(2)
            current_content = []
            continue
        
        # Regular content line
        if current_article:
            current_content.append(line)
    
    # Don't forget last article
    if current_article and current_content:
        articles.append({
            "chapter": current_chapter,
            "section": current_section,
            "article": current_article,
            "title": current_title,
            "content": "\n".join(current_content),
        })
    
    return articles


def main():
    """Crawl all priority laws and save as JSON."""
    print("🏛️ Legal AI — Law Crawler")
    print(f"Output directory: {DATA_DIR}")
    print(f"Laws to crawl: {len(PRIORITY_LAWS)}")
    print()
    
    for law_info in PRIORITY_LAWS:
        print(f"📜 {law_info['name']} ({law_info['number']})")
        
        output_file = DATA_DIR / f"{law_info['number'].replace('/', '_')}.json"
        
        if output_file.exists():
            print(f"  ✅ Already crawled, skipping")
            continue
        
        try:
            # Crawl
            page_data = crawl_law_page(law_info["url"])
            
            # Parse articles
            articles = parse_articles(page_data["text"])
            print(f"  📋 Parsed {len(articles)} articles")
            
            # Save
            result = {
                **law_info,
                "full_text": page_data["text"],
                "articles": articles,
                "article_count": len(articles),
                "word_count": len(page_data["text"].split()),
                "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ Saved to {output_file.name}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Be polite
        time.sleep(2)
    
    print("\n✅ Crawling complete!")


if __name__ == "__main__":
    main()
