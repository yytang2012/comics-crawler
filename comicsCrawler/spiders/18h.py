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


class Comics18HSpider(scrapy.Spider):
    """
    classdocs

    example: http://18h.mm-cg.com/18H_6694.html
    """
    dom = '18h.mm-cg.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(Comics18HSpider, self).__init__(*args, **kwargs)
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
        html = str(response.body)
        title = sel.xpath('//h1/text()').extract()[0]
        p = r'Large_cgurl\[\d+\] = "(http://[^\"]+)";'
        image_urls = re.findall(p, html)

        for idx, image_url in enumerate(image_urls):
            image_name = "{0}/{1:03d}.jpg".format(title, 1 + idx)
            image_name = os.path.join('18h', image_name)
            image_path = os.path.join(self.root_path, image_name)
            if os.path.isfile(image_path):
                continue
            item = ComicscrawlerItem()
            item['image_urls'] = [image_url]
            item['Referer'] = response.url
            item['image_name'] = image_name
            yield item

