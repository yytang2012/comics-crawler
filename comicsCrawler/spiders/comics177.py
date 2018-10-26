#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class Comics177Spider(ComicSpider):
    """
    classdocs

    example: http://www.177pic.info/html/2015/07/952461.html
    """
    allowed_domains = ['www.177pic.info']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = '177pic'

    def polish_url(self, url):
        url = url.strip('\n').strip()
        pattern = 'http://www.177pic.info/html/[\d|\/]+.html'
        url = re.search(pattern, url).group(0)
        return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = False
        image_urls = sel.xpath('//p/img/@src').extract()
        return image_urls, is_page

    def parse_next_page(self, response):
        sel = Selector(response)
        next_page = sel.xpath('//p/a[contains(text(), "下一页") or contains(text(), "下一頁")]/@href').extract()
        if next_page:
            next_page_url = next_page[0]
            next_page_url = response.urljoin(next_page_url.strip())
            return next_page_url
        else:
            return None


