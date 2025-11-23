import scrapy
from production_scraper.items import ProductionScraperItem
from production_scraper.spiders.base_spider import BaseSpider
import logging

logger = logging.getLogger(__name__)

class RobustSpider(BaseSpider):
    name = 'robust'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'production_scraper.middlewares.RandomUserAgentMiddleware': 400,
            'production_scraper.middlewares.ProxyMiddleware': 410,
        }
    }

    def __init__(self, start_url=None, job_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else getattr(self, 'start_urls', [])
        self.job_id = job_id or getattr(self, 'job_id', None)

    def parse(self, response):
        # discover sections (fallback to parsing links on the page)
        section_links = response.css('nav a::attr(href)').getall() or response.css('a::attr(href)').getall()
        for link in section_links:
            yield response.follow(link, callback=self.parse_section, meta={'section': link.split('/')[-1]})

    def parse_section(self, response):
        section = response.meta.get('section', 'unknown')
        # article links
        for article in response.css('a.article-link::attr(href)').getall():
            yield response.follow(article, callback=self.parse_article, meta={'section': section})

        # pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_section, meta={'section': section})

    def parse_article(self, response):
        item = ProductionScraperItem()
        item['job_id'] = self.job_id
        item['section'] = response.meta.get('section', 'unknown')
        item['title'] = response.css('h1::text').get() or ''
        item['text'] = ' '.join(response.css('div.content p::text').getall())
        item['image_urls'] = response.css('div.content img::attr(src)').getall()
        item['links'] = response.css('div.content a::attr(href)').getall()
        item['page_url'] = response.url
        item['status_code'] = response.status
        yield item
