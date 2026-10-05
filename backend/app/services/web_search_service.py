import urllib.request
import urllib.parse
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def search_official_schemes(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs real-time live online web search using DuckDuckGo search endpoint
        and returns structured title, live snippet content, and official links.
        """
        results = []
        try:
            # 1. Primary Live Search Query
            search_term = f"{query} India government scheme guidelines portal"
            data = urllib.parse.urlencode({'q': search_term}).encode('utf-8')
            
            req = urllib.request.Request(
                'https://lite.duckduckgo.com/lite/',
                data=data,
                headers={'User-Agent': self.user_agent}
            )

            with urllib.request.urlopen(req, timeout=7) as response:
                html = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                trs = soup.find_all('tr')
                i = 0
                while i < len(trs):
                    tr = trs[i]
                    a = tr.find('a', class_='result-link')
                    if a:
                        title = a.get_text(strip=True)
                        link = a.get('href', '')
                        snippet = ''
                        
                        # Look ahead for snippet text in following table rows
                        for j in range(1, 3):
                            if i + j < len(trs):
                                snip_td = trs[i+j].find('td', class_='result-snippet')
                                if snip_td:
                                    snippet = snip_td.get_text(strip=True)
                                    break
                        
                        if 'uddg=' in link:
                            match = re.search(r'uddg=([^&]+)', link)
                            if match:
                                link = urllib.parse.unquote(match.group(1))

                        if title and (snippet or link):
                            results.append({
                                "title": title,
                                "snippet": snippet,
                                "link": link,
                                "source": "Live Web Search"
                            })
                            if len(results) >= max_results:
                                break
                    i += 1

            # 2. Fallback GET query if POST returned empty
            if not results:
                encoded_q = urllib.parse.quote(query)
                req_get = urllib.request.Request(
                    f"https://html.duckduckgo.com/html/?q={encoded_q}",
                    headers={'User-Agent': self.user_agent}
                )
                with urllib.request.urlopen(req_get, timeout=6) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    for result_div in soup.find_all('div', class_='result'):
                        if len(results) >= max_results:
                            break
                        title_elem = result_div.find('a', class_='result__a')
                        snippet_elem = result_div.find('a', class_='result__snippet')
                        if title_elem and snippet_elem:
                            title = title_elem.get_text(strip=True)
                            snippet = snippet_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                            if 'uddg=' in link:
                                match = re.search(r'uddg=([^&]+)', link)
                                if match:
                                    link = urllib.parse.unquote(match.group(1))
                            results.append({
                                "title": title,
                                "snippet": snippet,
                                "link": link,
                                "source": "Live Web Search"
                            })

            return results

        except Exception as e:
            logger.error(f"Live web search execution failed: {e}")
            return []

web_search_service = WebSearchService()
