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
from scrapy import Request
from scrapy.selector import Selector

from comicsCrawler.items import ComicscrawlerItem
from comicsCrawler.spiders.private_data import e_hentai_cookies
from libs.misc import *


class EhentaiSpider(scrapy.Spider):
    """
    classdocs

    example: https://e-hentai.org/g/421552/4a24a76b83/
    """
    dom = 'e-hentai.org'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    handle_httpstatus_list = [404]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
    }

    def __init__(self, *args, **kwargs):
        super(EhentaiSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        self.headers = {"Referer": 'https://e-hentai.org/'}
        self.cookie_flag = True
        print(self.start_urls)

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            print(url)
            yield Request(url, callback=self.parse, headers=self.headers,
                          cookies=e_hentai_cookies, dont_filter=True)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'https://e-hentai.org/[\w]/421552/4a24a76b83'
        # url = re.search(pattern, url).group(0)
        suffix = '?nw=always'
        if url[-len(suffix):] != suffix:
            url += suffix
        return url

    def parse(self, response):
        if response.status == 404:
            self.cookie_flag = True
            request = scrapy.Request(response.url, callback=self.parse, headers=self.headers,
                                     cookies=e_hentai_cookies, dont_filter=True)
            yield request
        else:
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
                title = sel.xpath('//h1/text()').extract()[0]
                title = polish_string(title)

            if self.cookie_flag:
                image_web_urls = sel.xpath('//div[@id="gdt"]/div/a/@href').extract()
            else:
                image_web_urls = sel.xpath('//div[@id="gdt"]/div[@class="gdtm"]/div/a/@href').extract()

            for idx, image_web_url in enumerate(image_web_urls):
                image_name = "{0}/{1:03d}.jpg".format(title, start_image_index + idx)
                image_name = os.path.join('hentai', image_name)
                image_path = os.path.join(self.root_path, image_name)
                if os.path.isfile(image_path):
                    continue
                if self.cookie_flag:
                    request = scrapy.Request(image_web_url, callback=self.parse_image, headers=self.headers,
                                             cookies=e_hentai_cookies, dont_filter=True)
                else:
                    request = scrapy.Request(image_web_url, callback=self.parse_image, headers=self.headers)

                request.meta['image_name'] = image_name
                yield request

            no_next_page_sign = sel.xpath('//div[@class="gtb"]/table/tr/td[contains(text(), ">")]').extract()
            if len(no_next_page_sign) == 0:
                next_page_url = response.xpath('//div[@class="gtb"]/table//tr/td/a/@href').extract()[-1]
                next_page_url = response.urljoin(next_page_url.strip())
                request = scrapy.Request(next_page_url, callback=self.parse)
                request.meta[start_image_index_key] = len(image_web_urls) + start_image_index
                request.meta[title_key] = title
                yield request

    def parse_image(self, response):
        sel = Selector(response)
        option_sections = sel.xpath('//img').extract()
        image_url = ''
        for section in option_sections:
            keyword = 'id="img"'
            if keyword in section:
                pattern = 'src="([^"]+)"'
                image_url = re.search(pattern, section).group(1)
        item = ComicscrawlerItem()
        item['image_name'] = response.meta['image_name']
        item['Referer'] = response.url
        item['image_urls'] = [image_url]
        item['cookies'] = e_hentai_cookies
        yield item
