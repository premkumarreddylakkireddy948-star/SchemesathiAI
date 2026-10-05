import urllib.request
import urllib.parse
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

OFFICIAL_GOVT_DOMAINS_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".ap.gov.in",
    "jnanabhumi.ap.gov.in",
    "epass.apcfss.in",
    "apcfss.in",
    ".tn.gov.in",
    "india.gov.in",
    "myschemes.gov.in",
    "scholarships.gov.in",
    "aicte-india.org",
    "mudra.org.in",
    "jansuraksha.gov.in",
    "maandhan.in",
    "vidyalakshmi.co.in",
    "pmkvyofficial.org",
    "nrlm.gov.in",
    "indiapost.gov.in",
    "kviconline.gov.in",
    "pmsuryaghar.gov.in",
    "pmvishwakarma.gov.in"
)

def is_official_government_domain(url: str) -> bool:
    """Strictly checks whether a given URL belongs to an official government domain."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        if netloc.startswith("www."):
            netloc = netloc[4:]
        
        if netloc.endswith(".gov.in") or netloc.endswith(".nic.in"):
            return True
            
        for official_domain in OFFICIAL_GOVT_DOMAINS_SUFFIXES:
            if netloc == official_domain or netloc.endswith("." + official_domain):
                return True
        return False
    except Exception:
        return False

class WebSearchService:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def search_official_schemes(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs real-time live online web search using DuckDuckGo search endpoint
        and returns structured title, live snippet content, and official links.
        Prioritizes official government (.gov.in, .nic.in, official ministry) domains.
        """
        results = []
        try:
            # Detect target state in query
            q_lower = query.lower()
            state_target = ""
            if "andhra" in q_lower or "ap" in q_lower:
                state_target = "site:ap.gov.in OR site:gov.in"
            elif "tamil nadu" in q_lower or "tn" in q_lower:
                state_target = "site:tn.gov.in OR site:gov.in"

            search_term = f"{query} {state_target} official government portal guidelines" if state_target else f"{query} site:gov.in OR site:nic.in official government portal guidelines"
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
                            is_official = is_official_government_domain(link)
                            results.append({
                                "title": title,
                                "snippet": snippet,
                                "link": link,
                                "is_official": is_official,
                                "source": "Official Government Portal" if is_official else "Third-Party Reference"
                            })
                            if len(results) >= max_results * 2:
                                break
                    i += 1

            if not results:
                encoded_q = urllib.parse.quote(f"{query} official government portal")
                req_get = urllib.request.Request(
                    f"https://html.duckduckgo.com/html/?q={encoded_q}",
                    headers={'User-Agent': self.user_agent}
                )
                with urllib.request.urlopen(req_get, timeout=6) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    for result_div in soup.find_all('div', class_='result'):
                        if len(results) >= max_results * 2:
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
                            is_official = is_official_government_domain(link)
                            results.append({
                                "title": title,
                                "snippet": snippet,
                                "link": link,
                                "is_official": is_official,
                                "source": "Official Government Portal" if is_official else "Third-Party Reference"
                            })

            results.sort(key=lambda x: 0 if x.get("is_official") else 1)
            return results[:max_results]

        except Exception as e:
            logger.error(f"Live web search execution failed: {e}")
            return []

web_search_service = WebSearchService()
