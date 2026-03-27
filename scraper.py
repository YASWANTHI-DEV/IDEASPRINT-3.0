import requests
from bs4 import BeautifulSoup

def search_web(query):
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        blocks = soup.find_all("div", class_="result")

        for block in blocks[:5]:
            title_tag = block.find("a", class_="result__a")
            snippet_tag = block.find("a", class_="result__snippet") or block.find("div", class_="result__snippet")

            title = title_tag.get_text(" ", strip=True) if title_tag else "No Title"
            snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else "No snippet available"
            link = title_tag.get("href") if title_tag else ""

            results.append({
                "title": title,
                "snippet": snippet,
                "link": link
            })

        if not results:
            results.append({
                "title": "Fallback Data",
                "snippet": "Market is growing with increasing demand and competition.",
                "link": ""
            })

        return results

    except Exception as e:
        return [{
            "title": "Error",
            "snippet": f"Unable to fetch live data. Error: {e}",
            "link": ""
        }]