#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class Xesn8Spider(ComicSpider):
    """
    classdocs

    example: http://www.xesn8.com/snmh/v15394.html
    """
    allowed_domains = ['www.xesn8.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = '少女邪恶漫画'

    def polish_url(self, url):
        url = url.strip('\n').strip()
        pattern = 'http://www.xesn8.com/snmh/v([\d]+)'
        url = 'http://www.xesn8.com/snmh/v{}.html'.format(re.search(pattern, url).group(1))
        return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = True
        page_info = sel.xpath('//div[@class="inc_page"]/a/text()').extract()[0]
        page_number = int(re.search('共([\d]+)页', page_info).group(1))
        pattern = 'http://www.xesn8.com/snmh/v([\d]+)'
        comic_id = re.search(pattern, response.url).group(1)
        page_urls = ['http://www.xesn8.com/snmh/v{}.html'.format(comic_id)]
        for page in range(2, page_number+1):
            page_urls.append('http://www.xesn8.com/snmh/v{}_{}.html'.format(comic_id, page))
        return page_urls, is_page

    def parse_image(self, response):
        sel = Selector(response)
        meta = response.meta
        item = meta['item']
        item['Referer'] = response.url

        image_url = sel.xpath('//div[@class="ny"]/a/img/@src').extract()[0]
        image_url = response.urljoin(image_url)
        item['image_urls'] = [image_url]
        yield item
