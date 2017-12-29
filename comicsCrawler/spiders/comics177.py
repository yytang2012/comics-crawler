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


class Comics177Spider(scrapy.Spider):
    """
    classdocs

    example: http://www.177pic.info/html/2015/07/952461.html
    """
    dom = 'www.177pic.info'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(Comics177Spider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        pattern = 'http://www.177pic.info/html/[\d|\/]+.html'
        url = re.search(pattern, url).group(0)
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
            ss = sel.xpath('//h1/text()').extract()[0]
            title = ss.replace(u'[中文]', '')

        image_urls = sel.xpath('//img/@src').extract()
        image_number = len(image_urls)
        for picture_index in range(0, image_number):
            image_name = "{0}/{1:03d}.jpg".format(title, start_image_index + picture_index)
            image_path = os.path.join(self.root_path, image_name)
            if os.path.isfile(image_path):
                continue
            item = ComicscrawlerItem()
            item['image_urls'] = [image_urls[picture_index]]
            item['Referer'] = response.url
            item['image_name'] = image_name
            yield item

        aa = sel.xpath('//p/a')
        for a in aa:
            tmp = a.xpath('text()').extract()
            if tmp != [] and (tmp[0] == u'下一页' or tmp[0] == u'下一頁'):
                next_page_url = a.xpath('@href').extract()[0]
                next_page_url = response.urljoin(next_page_url.strip())
                request = scrapy.Request(next_page_url, callback=self.parse)
                request.meta[start_image_index_key] = image_number + start_image_index
                request.meta[title_key] = title
                yield request
