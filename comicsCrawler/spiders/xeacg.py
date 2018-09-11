#!/usr/bin/env python
# coding=utf-8

from scrapy.selector import Selector

from comicsCrawler.spiders.comic_spider import ComicSpider
from libs.misc import *


class XeacgSpider(ComicSpider):
    """
    classdocs

    example: http://www.xeacg.org/shaonv/2017/0316/v4508.html
    """
    allowed_domains = ['www.xeacg.org']
    name = get_spider_name_from_domain(allowed_domains[0])
    comic_name = '邪恶ACG'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
    }

    def polish_url(self, url):
        url = url.strip('\n').strip()
        pattern = 'http://www.xeacg.org/shaonv/[\d]+/[\d]+/v[\d]+'
        url = '{}.html'.format(re.search(pattern, url).group(0))
        return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_string(title)
        return title

    def parse_page(self, response):
        sel = Selector(response)
        is_page = True
        page_info = sel.xpath('//ul[@class="pagelist"]/li/a/text()').extract()[0]
        page_number = int(re.search('共([\d]+)页', page_info).group(1))
        pattern = 'http://www.xeacg.org/shaonv/[\d]+/[\d]+/v[\d]+'
        prefix = re.search(pattern, response.url).group(0)
        page_urls = ['{}.html'.format(prefix)]
        for page in range(2, page_number+1):
            page_urls.append('{}_{}.html'.format(prefix, page))
        return page_urls, is_page

    def parse_image(self, response):
        sel = Selector(response)
        meta = response.meta
        item = meta['item']
        item['Referer'] = response.url

        image_url = sel.xpath('//li[@id="imgshow"]/img/@src').extract()[0]
        image_url = response.urljoin(image_url)
        item['image_urls'] = [image_url]
        yield item
