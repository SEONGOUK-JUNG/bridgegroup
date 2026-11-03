"""Validate published search metadata, structured facts and local assets."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote

docs = Path(__file__).resolve().parents[1] / 'docs'
pages = [p for p in docs.rglob('index.html')]
assert len(pages) == 17
urls = set()
for page in pages:
    doc = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    assert doc.title and doc.title.string
    assert len(doc.select('meta[name="description"]')) == 1
    assert len(doc.select('link[rel="canonical"]')) == 1
    canonical = doc.select_one('link[rel="canonical"]')['href']
    assert canonical not in urls
    urls.add(canonical)
    alternates = doc.select('link[hreflang]')
    assert len(alternates) == 18
    assert len({a['hreflang'] for a in alternates}) == 18
    graph = json.loads(doc.select_one('script[type="application/ld+json"]').string)
    assert graph['@context'] == 'https://schema.org'
    items = graph['@graph'][3]['itemListElement']
    assert len(items) == 6
    assert 'water' in items[3]['item']['description'].lower() or doc.html['lang'] != 'en'
    assert len(doc.select('h1')) == 1
    for tag, attr in [('img','src'),('script','src'),('link','href')]:
        for el in doc.select(f'{tag}[{attr}]'):
            value = el[attr]
            parsed = urlparse(value)
            if parsed.scheme or value.startswith('//') or not parsed.path:
                continue
            target = docs / unquote(parsed.path.lstrip('/')) if value.startswith('/') else page.parent / unquote(parsed.path)
            assert target.exists(), (page, value)
ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
root = ET.parse(docs/'sitemap.xml').getroot()
assert {e.text for e in root.findall('s:url/s:loc', ns)} == urls
assert (docs/'CNAME').read_text().strip() == 'bridgegroup.asia'
assert 'Sitemap: https://bridgegroup.asia/sitemap-index.xml' in (docs/'robots.txt').read_text()
index = ET.parse(docs/'sitemap-index.xml').getroot()
assert index.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex'
assert [e.text for e in index.findall('s:sitemap/s:loc', ns)] == ['https://bridgegroup.asia/sitemap.xml']
print('PASS: 17 language pages, metadata, 18 hreflangs each, JSON-LD, sitemap and referenced local assets.')

text_urls=(docs/'sitemap.txt').read_text(encoding='utf-8').splitlines()
assert len(text_urls)==17 and set(text_urls)==urls
print('PASS: URL-only text sitemap matches all 17 canonical language URLs.')
