
import requests
import json
import re
import time

class TenderScraper:
    def __init__(self, firecrawl_url="http://localhost:3002", serper_api_key="0a795266607d2956b3d531b4fa468b2e9cd3df28"):
        self.firecrawl_url = firecrawl_url
        self.serper_api_key = serper_api_key
        self.fc_endpoints = ["/scrape", "/v1/scrape", "/crawl", "/v0/scrape"]

    def _try_fc_post(self, endpoint, payload):
        full_url = f"{self.firecrawl_url}{endpoint}"
        # Increased timeout to 60 seconds for slow government portals
        timeout = 60 
        
        for attempt in range(2): # Try twice
            try:
                response = requests.post(full_url, json=payload, timeout=timeout)
                if response.status_code == 200:
                    return response.json()
                print(f"Attempt {attempt+1}: Server returned {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"Attempt {attempt+1}: Request timed out after {timeout}s")
            except Exception as e:
                print(f"Attempt {attempt+1}: Error {e}")
                break # Stop on critical errors
        return None

    def crawl_portal(self, portal_url):
        print(f"Crawling portal: {portal_url}...")
        payload = {"url": portal_url, "pageOptions": {"onlyMainContent": False}}
        for endpoint in self.fc_endpoints:
            result = self._try_fc_post(endpoint, payload)
            if result:
                data = result.get("data", result)
                content = data.get("content", data.get("markdown", ""))
                links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
                tender_links = []
                keywords = ["tender", "bid", "rfp", "opportunity", "announcement", "مناقصة", "عطاء", "فرصة", "إعلان", "procurement", "supply", "شراء"]
                for title, url in links:
                    url_lower = url.lower()
                    title_lower = title.lower()
                    if any(k in url_lower or k in title_lower for k in keywords):
                        if not any(x in url_lower for x in ["login.php", "register.php", "contact.php", "about"]):
                            tender_links.append({"title": title, "url": url})
                if tender_links:
                    return tender_links
                if any(k in content.lower() for k in keywords):
                    return [{"title": "Main Portal Page", "url": portal_url}]
        return []

    def search_tenders(self, query, sources=None):
        all_results = []
        seen_urls = set()
        
        # If no sources provided, fallback to broad gov.eg search
        if not sources:
            print(f"Broad searching via Serper.dev: {query}...")
            search_queries = [f'"{query}" (tender OR bid OR RFP OR مناقصة OR عطاء) site:gov.eg']
        else:
            # Targeted search: one query per portal source
            print(f"Performing targeted search across {len(sources)} portals...")
            search_queries = []
            for source in sources:
                # Clean URL to get domain (e.g., https://etenders.gov.eg/path -> etenders.gov.eg)
                domain = source.split('//')[-1].split('/')[0].strip()
                if domain:
                    search_queries.append(f'"{query}" (tender OR bid OR RFP OR مناقصة OR عطاء) site:{domain}')

        url = "https://google.serper.dev/search"
        headers = {'X-API-KEY': self.serper_api_key, 'Content-Type': 'application/json'}

        for q in search_queries:
            try:
                payload = {"q": q, "gl": "eg", "hl": "en"}
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    organic = response.json().get("organic", [])
                    for r in organic:
                        link = r.get("link")
                        if link and link not in seen_urls:
                            all_results.append({ "url": link, "title": r.get("title") })
                            seen_urls.add(link)
            except Exception as e:
                print(f"Error searching for query {q}: {e}")
        
        return all_results[:20] # Return top 20 aggregated results

    def clean_content(self, text):
        if not text: return ""
        noise_patterns = [
            r"Back\s*", r"Haven\'t\s+decided\s+yet.*Still\s+unsure\?.*",
            r"Subscribe\s+to\s+our\s+updates.*Submit",
            r"©\s*\d{4}\s*HAFIZ\..*All\s+Rights\s+Reserved",
            r"Ask\s+me\s+anything.*", r"Passer\s+directement\s+au\s+contenu\s+principal.*",
            r"Toutes\s+les\s+langues.*", r"Botsonic \| Writesonic.*"
        ]
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    def get_tender_details(self, url):
        print(f"Extracting details via Firecrawl from: {url}...")
        payload = {"url": url, "pageOptions": {"onlyMainContent": True}}
        for endpoint in self.fc_endpoints:
            result = self._try_fc_post(endpoint, payload)
            if result:
                data = result.get("data", result)
                content = data.get("content", data.get("markdown", ""))
                return self.clean_content(content)
        return ""
