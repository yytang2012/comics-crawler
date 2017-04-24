# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class ComicscrawlerPipeline(ImagesPipeline):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Accept-Language": "zh-tw,zh;q=0.8,en-us;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate"
    }

    def process_item(self, item, spider):
        return super(ComicscrawlerPipeline, self).process_item(item, spider)

    def get_media_requests(self, item, info):
        print("get_media_requests")
        headers = {}
        for key in self.default_headers:
            if key not in headers:
                headers[key] = self.default_headers[key]
        headers["Referer"] = item['Referer']
        return [scrapy.Request(x, headers=headers, meta={'image_name': item['image_name']})
                for x in item.get('image_urls', [])]

    def get_images(self, response, request, info):
        print("get_images")

        for key, image, buf, in super(ComicscrawlerPipeline, self).get_images(response, request, info):
            key = self.change_filename(key, response)
            yield key, image, buf

    def change_filename(self, key, response):
        return "{0}".format(response.meta['image_name'])
