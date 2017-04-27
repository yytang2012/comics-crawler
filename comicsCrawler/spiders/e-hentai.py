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


class EhentaiSpider(scrapy.Spider):
    """
    classdocs

    example: https://e-hentai.org/g/421552/4a24a76b83/
    """
    dom = 'e-hentai.org'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(EhentaiSpider, self).__init__(*args, **kwargs)
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'https://e-hentai.org/[\w]/421552/4a24a76b83'
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
            ss = sel.xpath('//h1/text()').extract()[0]
            title = ss.replace(u'[中文]', '')

        image_web_urls = sel.xpath('//div[@class="gdtm"]/div/a/@href').extract()
        for idx, image_web_url in enumerate(image_web_urls):
            request = scrapy.Request(image_web_url, callback=self.parse_image)
            request.meta['image_name'] = "{0}/{1:03d}.jpg".format(title, start_image_index + idx)
            yield request

        no_next_page_sign = sel.xpath('//td[@class="ptdd"]/text()').extract()
        if len(no_next_page_sign) == 0 or no_next_page_sign[0] != u'>':
            next_page_url = response.xpath('//table[@class="ptb"]/tr/td/a/@href').extract()[-1]
            next_page_url = response.urljoin(next_page_url.strip())
            request = scrapy.Request(next_page_url, callback=self.parse)
            request.meta[start_image_index_key] = len(image_web_urls) + start_image_index
            request.meta[title_key] = title
            yield request

    def parse_image(self, response):
        sel = Selector(response)
        image_url = sel.xpath('//img/@src').extract()[4]
        item = ComicscrawlerItem()
        item['image_name'] = response.meta['image_name']
        item['Referer'] = response.url
        item['image_urls'] = [image_url]
        yield item
