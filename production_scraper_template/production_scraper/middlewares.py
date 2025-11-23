import random
from scrapy import signals

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117 Safari/537.36'
]

class RandomUserAgentMiddleware:
    def process_request(self, request, spider):
        ua = random.choice(USER_AGENTS)
        request.headers.setdefault('User-Agent', ua)

# Proxy middleware placeholder (implement your proxy provider logic here)
class ProxyMiddleware:
    def process_request(self, request, spider):
        proxy = spider.settings.get('PROXY')
        if proxy:
            request.meta['proxy'] = proxy
