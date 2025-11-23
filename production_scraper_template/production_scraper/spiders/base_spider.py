import scrapy
import hashlib
from urllib.parse import urljoin, urlparse

class BaseSpider(scrapy.Spider):
    # helpers: canonicalize URLs, fingerprint, politeness helper
    def canonicalize(self, url, base=None):
        if base:
            url = urljoin(base, url)
        parsed = urlparse(url)
        # simple canonicalization: lower host, strip fragment
        canonical = parsed._replace(fragment='').geturl()
        return canonical

    def fingerprint(self, url):
        # stable fingerprint for dedupe
        h = hashlib.sha256()
        h.update(url.encode('utf-8'))
        return h.hexdigest()
