
import os
import requests
from dataclasses import dataclass
from typing import Optional
from bs4 import BeautifulSoup

@dataclass
class ArticleInfo:
    title: str
    author: str
    content: str
    url: str
    description: Optional[str] = None

class ContentExtractor:
    def __init__(self):
        self.jina_reader_base_url = "https://r.jina.ai/"

    def extract(self, url: str) -> ArticleInfo:
        jina_url = f"{self.jina_reader_base_url}{url}"
        
        try:
            response = requests.get(jina_url, timeout=30)
            response.raise_for_status()
            content = response.text
            
            metadata = self._get_metadata(url)
            
            return ArticleInfo(
                title=metadata.get('title', 'Untitled'),
                author=metadata.get('author', 'Unknown'),
                content=content,
                url=url,
                description=metadata.get('description')
            )
            
        except Exception as e:
            print(f"Jina Reader extraction failed: {e}. Falling back to basic requests.")
            raise e

    def _get_metadata(self, url: str) -> dict:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else 'Untitled'
            
            author = 'Unknown'
            if 'weixin.qq.com' in url:
                author_tag = soup.find(class_='profile_nickname') or soup.find(id='js_name')
                if author_tag:
                    author = author_tag.get_text(strip=True)
            
            if author == 'Unknown':
                author_meta = soup.find('meta', attrs={'name': 'author'})
                if author_meta:
                    author = author_meta.get('content')
            
            description = ''
            desc_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if desc_meta:
                description = desc_meta.get('content')
                
            return {
                'title': title,
                'author': author,
                'description': description
            }
        except Exception as e:
            print(f"Metadata extraction failed: {e}")
            return {'title': 'Untitled', 'author': 'Unknown'}

