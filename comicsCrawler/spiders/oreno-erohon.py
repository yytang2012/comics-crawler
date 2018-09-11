#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class OrenoErohonSpider(ComicSpider):
    """
    classdocs

    example: http://oreno-erohon.com/?p=121942
    """
    allowed_domains = ['oreno-erohon.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = 'oreno-erohon'

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = False
        image_urls = sel.xpath('//section[@class="entry-content"]/img/@src').extract()
        return image_urls, is_page

