#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class TemplateSpider(ComicSpider):
    """
    classdocs

    example: https://www.wnacg.org/photos-index-aid-57940.html
    """
    allowed_domains = ['www.example.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = 'example'

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'http://www.177pic.info/html/[\d|\/]+.html'
        # url = re.search(pattern, url).group(0)
        return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = True
        page_urls = sel.xpath('//div[@class="pic_box"]/a/@href').extract()
        return page_urls, is_page

    def parse_next_page(self, response):
        sel = Selector(response)
        next_page = sel.xpath('//span[@class="next"]/a/@href').extract()
        if next_page:
            next_page_url = next_page[0]
            next_page_url = response.urljoin(next_page_url.strip())
            return next_page_url
        else:
            return None

    def parse_image(self, response):
        sel = Selector(response)
        meta = response.meta
        item = meta['item']
        item['Referer'] = response.url

        image_url = sel.xpath('//div[@id="posselect"]/img/@src').extract()[0]
        image_url = response.urljoin(image_url)
        item['image_urls'] = [image_url]
        yield item
