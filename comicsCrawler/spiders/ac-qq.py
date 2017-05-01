#!/usr/bin/env python
# coding=utf-8
"""
Created on April 24, 2017

@author: yytang

1. get the first page url
2. get the pictures of the current page
3. get the next page url
"""
import base64

import scrapy
from scrapy.selector import Selector

from comicsCrawler.items import ComicscrawlerItem
from libs.misc import *


class EhentaiSpider(scrapy.Spider):
    """
    classdocs

    example: http://ac.qq.com/Comic/comicInfo/id/17114
    """
    dom = 'ac.qq.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.1,
    # }

    def __init__(self, *args, **kwargs):
        super(EhentaiSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        # pattern = 'https://e-hentai.org/[\w]/421552/4a24a76b83'
        # url = re.search(pattern, url).group(0)
        return url

    def parse(self, response):
        sel = Selector(response)
        title = sel.xpath('//h2[@class="works-intro-title ui-left"]/strong/text()').extract()[0]
        episode_selectors = sel.xpath('//li/p/span[@class="works-chapter-item"]/a')
        for episode_selector in episode_selectors:
            subtitle = episode_selector.xpath('@title').extract()[0]
            url = episode_selector.xpath('@href').extract()[0]
            url = response.urljoin(url)
            request = scrapy.Request(url, callback=self.parse_page_one)
            request.meta['title'] = '{0}/{1}'.format(title, subtitle)
            yield request

    def parse_page_one(self, response):
        title = response.meta['title']
        refUrl = response.url
        sel = Selector(response)
        section = sel.xpath('//script[contains(text(), "DATA")]').extract()[0]
        encrpted_data = section.split('\'')[1][1:]
        detail_list = json.loads(base64.b64decode(encrpted_data).decode())['picture']
        urls = [pic['url'] for pic in detail_list]

        for idx, url in enumerate(urls):
            img_name = "{0}/{1:03d}.jpg".format(title, idx + 1)
            img_path = os.path.join(self.root_path, img_name)
            if os.path.isfile(img_path):
                continue
            item = ComicscrawlerItem()
            item['image_urls'] = [url]
            item['Referer'] = refUrl
            item['image_name'] = img_name
            yield item
