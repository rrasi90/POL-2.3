import urllib.request
import urllib.parse
import re
import json

def search_ddg(query, max_results=10):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'<a[^>]+class="result__url"[^>]+href="([^"]+)"', html)
            snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            results = []
            for i, href in enumerate(matches):
                if 'uddg=' in href:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    actual_url = parsed.get('uddg', [href])[0]
                else:
                    actual_url = href
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
                results.append({'url': actual_url, 'snippet': snippet})
                if len(results) >= max_results:
                    break
            return results
    except Exception as e:
        print('Error:', e)
        return []

res = search_ddg('OmniRetail Nigeria B2B TechCrunch Deepankar Rustagi')
print(f"Found {len(res)} results:")
for r in res[:5]:
    print(" -", r['url'], "::", r['snippet'][:80])
