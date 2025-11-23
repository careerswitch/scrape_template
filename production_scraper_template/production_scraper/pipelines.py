import os
import io
import hashlib
from supabase import create_client
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings
import logging

logger = logging.getLogger(__name__)

class SupabasePipeline:
    def __init__(self, supabase_url, supabase_key):
        self.supabase = create_client(supabase_url, supabase_key)

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings.get('SUPABASE_URL')
        key = crawler.settings.get('SUPABASE_KEY')
        return cls(url, key)

    def process_item(self, item, spider):
        try:
            data = {
                'job_id': item.get('job_id'),
                'url': item.get('page_url'),
                'title': item.get('title'),
                'body_text': item.get('text'),
                'domain': spider.allowed_domains[0] if spider.allowed_domains else None,
                'status_code': item.get('status_code'),
                'links': item.get('links'),
            }
            # Upsert into pages table
            res = self.supabase.table('pages').upsert(data).execute()
            # check errors
            if res.error:
                logger.error('Supabase upsert error: %s', res.error)
        except Exception as e:
            logger.exception('Supabase pipeline error')
        return item

class SupabaseStorageImagesPipeline(ImagesPipeline):
    def __init__(self, store_uri, supabase_url, supabase_key, bucket):
        super().__init__(store_uri)
        self.supabase = create_client(supabase_url, supabase_key)
        self.bucket = bucket

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings.get('IMAGES_STORE', 'images')
        return cls(store_uri, settings.get('SUPABASE_URL'), settings.get('SUPABASE_KEY'), settings.get('SUPABASE_IMAGES_BUCKET'))

    def get_media_requests(self, item, info):
        for url in item.get('image_urls', []):
            yield scrapy.Request(url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta.get('item')
        section = item.get('section', 'unknown')
        filename = request.url.split('/')[-1].split('?')[0]
        return f"{section}/{filename}"

    def item_completed(self, results, item, info):
        # Upload to Supabase Storage using returned image bytes
        uploaded_paths = []
        for ok, data in results:
            if not ok:
                continue
            path = data.get('path')
            uploaded_paths.append(path)
        # Note: ImagesPipeline already stores locally; if you prefer stream-to-supabase,
        # override the media download handlers to capture the bytes and call supabase.storage.upload
        item['images'] = uploaded_paths
        return item
