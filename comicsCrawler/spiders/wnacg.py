#!/usr/bin/env python
# coding=utf-8
"""
Created on April 24, 2017

@author: yytang

1. get the first page url
2. get the pictures of the current page
3. get the next page url
"""

import scrapy
from scrapy.selector import Selector

from comicsCrawler.items import ComicscrawlerItem
from libs.misc import *


class WnacgSpider(scrapy.Spider):
    """
    classdocs

    example: https://www.wnacg.org/photos-index-aid-57940.html
    """
    dom = 'www.wnacg.org'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(WnacgSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'http://www.177pic.info/html/[\d|\/]+.html'
        # url = re.search(pattern, url).group(0)
        return url

    def parse(self, response):
        sel = Selector(response)
        start_image_index_key = 'start_index'
        if start_image_index_key in response.meta:
            start_image_index = response.meta[start_image_index_key]
        else:
            start_image_index = 1

        title_key = 'comics_title'
        if title_key in response.meta:
            title = response.meta[title_key]
        else:
            title = sel.xpath('//h2/text()').extract()[0]

        page_urls = sel.xpath('//div[@class="pic_box"]/a/@href').extract()
        for picture_index, page_url in enumerate(page_urls):
            image_name = "{0}/{1:03d}.jpg".format(title, start_image_index + picture_index)
            image_name = os.path.join('绅士漫画', image_name)
            image_path = os.path.join(self.root_path, image_name)
            if os.path.isfile(image_path):
                continue
            request = scrapy.Request(response.urljoin(page_url), callback=self.parse_image)
            request.meta['image_name'] = image_name
            yield request

        next_page = sel.xpath('//span[@class="next"]/a/@href').extract()
        if next_page:
            next_page_url = next_page[0]
            next_page_url = response.urljoin(next_page_url.strip())
            request = scrapy.Request(next_page_url, callback=self.parse)
            request.meta[start_image_index_key] = len(page_urls) + start_image_index
            request.meta[title_key] = title
            yield request

    def parse_image(self, response):
        sel = Selector(response)
        meta = response.meta
        image_name = meta['image_name']
        item = ComicscrawlerItem()
        item['Referer'] = response.url
        item['image_name'] = image_name

        image_url = sel.xpath('//div[@id="posselect"]/img/@src').extract()[0]
        image_url = response.urljoin(image_url)
        item['image_urls'] = [image_url]
        yield item
