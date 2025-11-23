import os

BOT_NAME = 'production_scraper'
SPIDER_MODULES = ['production_scraper.spiders']
NEWSPIDER_MODULE = 'production_scraper.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', '8'))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv('CONCURRENT_REQUESTS_PER_DOMAIN', '2'))
DOWNLOAD_DELAY = float(os.getenv('DOWNLOAD_DELAY', '0.5'))
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = float(os.getenv('AUTOTHROTTLE_START_DELAY', '0.5'))
AUTOTHROTTLE_MAX_DELAY = float(os.getenv('AUTOTHROTTLE_MAX_DELAY', '10'))
RETRY_ENABLED = True
RETRY_TIMES = 5

# scrapy-redis scheduler (use the maintained implementation you choose)
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
SCHEDULER_PERSIST = True
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# pipelines
ITEM_PIPELINES = {
    'production_scraper.pipelines.SupabasePipeline': 300,
    'production_scraper.pipelines.SupabaseStorageImagesPipeline': 200,
}

# Supabase settings (set via env / K8s secrets)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_IMAGES_BUCKET = os.getenv('SUPABASE_IMAGES_BUCKET', 'scraped-images')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Prometheus exporter port (if using built-in metrics)
PROMETHEUS_METRICS_PORT = int(os.getenv('PROMETHEUS_METRICS_PORT', '8000'))
