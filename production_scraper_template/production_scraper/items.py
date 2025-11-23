import scrapy

class ProductionScraperItem(scrapy.Item):
    job_id = scrapy.Field()
    section = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    page_url = scrapy.Field()
    links = scrapy.Field()
    status_code = scrapy.Field()
