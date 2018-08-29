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


class CartoonmadSpider(scrapy.Spider):
    """
    classdocs

    example: https://www.cartoonmad.com/comic/119400011126001.html
    """
    dom = 'www.cartoonmad.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.3,
    # }

    def __init__(self, *args, **kwargs):
        super(CartoonmadSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'https://e-hentai.org/[\w]/421552/4a24a76b83'
        # url = re.search(pattern, url).group(0)
        return url

    def get_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//title/text()').extract()[0]
        title = title.split('-')[0].strip()
        return title

    def get_episodes(self, response):
        sel = Selector(response)
        episodes = []
        aa = sel.xpath('//tr/td/a')

        def episode_filter(s):
            p = 'href=\"/comic/\d{6,}.html'
            return True if re.search(p, s) else False

        aa = [a for a in aa if episode_filter(a.extract())]
        for a in aa:
            episode_url = a.xpath('@href').extract()[0]
            episode_url = response.urljoin(episode_url)
            episode_title = a.xpath('text()').extract()[0]
            episodes.append((episode_url, episode_title))
        return episodes

    def parse(self, response):
        title = self.get_title(response)
        episodes = self.get_episodes(response)

        for episode_url, episode_title in episodes:
            request = scrapy.Request(episode_url, callback=self.parse_image)
            request.meta['title'] = '{0}/{1}'.format(title, episode_title)
            request.meta['page_id'] = 1
            yield request


    def parse_image(self, response):
        title = response.meta['title']
        page_id = response.meta['page_id']
        image_name = '{0}/{1:03d}.jpg'.format(title, page_id)
        image_name = os.path.join('cartoonmad', image_name)
        image_path = os.path.join(self.root_path, image_name)
        html = str(response.body)
        if not os.path.isfile(image_path):
            image_url = re.search('img src="(http://[\w.]*?cartoonmad\.com.+?)"', html).group(1)
            item = ComicscrawlerItem()
            item['image_name'] = image_name
            item['Referer'] = response.url
            item['image_urls'] = [image_url]
            yield item

        match = re.search('a href="(\d+[^"]*)', html)
        if match:
            next_page_url = response.urljoin(match.group(1))
            request = scrapy.Request(next_page_url, callback=self.parse_image)
            request.meta['title'] = title
            request.meta['page_id'] = page_id + 1
            yield request
