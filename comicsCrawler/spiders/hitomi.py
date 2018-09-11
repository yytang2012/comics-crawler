#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class HitomiSpider(ComicSpider):
    """
    classdocs

    example: https://hitomi.la/galleries/1285244.html
    """
    allowed_domains = ['hitomi.la']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = 'hitomi'

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/a/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        html = str(response.body.decode('utf-8'))
        pattern = '\'//tn.hitomi.la/smalltn/(.+)\.jpg\''
        image_urls = re.findall(pattern, html)
        image_urls = ['https://aa.hitomi.la/galleries/' + image_url for image_url in image_urls]
        is_page = False
        return image_urls, is_page


