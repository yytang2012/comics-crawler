#!/usr/bin/env python
# coding=utf-8
"""
Created on Sep 11, 2018

@author: yytang

1. get the first page url
2. get the pictures of the current page
3. get the next page url
"""
import abc
import scrapy
from comicsCrawler.items import ComicscrawlerItem
from libs.misc import *


class ComicSpider(scrapy.Spider):
    """
    classdocs

    example: https://www.wnacg.org/photos-index-aid-57940.html
    """
    dom = 'www.comics.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    comic_name = ''

    @abc.abstractmethod
    def parse_title(self, response):
        return ''

    @abc.abstractmethod
    def parse_page(self, response):
        return [], None

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'http://www.177pic.info/html/[\d|\/]+.html'
        # url = re.search(pattern, url).group(0)
        return url

    def parse_next_page(self, response):
        return None

    def parse_image(self, response):
        yield None

    def __init__(self, *args, **kwargs):
        super(ComicSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def parse(self, response):
        start_image_index_key = 'start_index'
        if start_image_index_key in response.meta:
            start_image_index = response.meta[start_image_index_key]
        else:
            start_image_index = 1

        title_key = 'comics_title'
        if title_key in response.meta:
            title = response.meta[title_key]
        else:
            title = self.parse_title(response)

        page_urls, is_page = self.parse_page(response)

        for picture_index, page_url in enumerate(page_urls):
            page_url = response.urljoin(page_url)
            image_name = "{0}/{1:03d}.jpg".format(title, start_image_index + picture_index)
            image_name = os.path.join(self.comic_name, image_name)
            image_path = os.path.join(self.root_path, image_name)
            if os.path.isfile(image_path):
                continue
            item = ComicscrawlerItem()
            item['Referer'] = response.url
            item['image_name'] = image_name

            if is_page:
                request = scrapy.Request(page_url, callback=self.parse_image)
                request.meta['item'] = item
                yield request
            else:
                item['image_urls'] = [page_url]
                yield item

        next_page_url = self.parse_next_page(response)
        if next_page_url:
            request = scrapy.Request(next_page_url, callback=self.parse)
            request.meta[start_image_index_key] = len(page_urls) + start_image_index
            request.meta[title_key] = title
            yield request
