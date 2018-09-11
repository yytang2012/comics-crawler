#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class NijibondoSpider(ComicSpider):
    """
    classdocs

    example: http://nijibondo.com/wp/hentai-oyasannokaori
    """
    allowed_domains = ['nijibondo.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = 'nijibondo'

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = False
        image_urls = sel.xpath('//div[@id="the-content"]/p/a/@href').extract()
        return image_urls, is_page

    def parse_next_page(self, response):
        return None

