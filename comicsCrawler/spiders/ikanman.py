#!/usr/bin/env python
# coding=utf-8
"""
Created on Dec 25, 2015

@author: yytang
"""

import execjs
import scrapy
from scrapy.selector import Selector

from comicsCrawler.items import ComicscrawlerItem
from libs.misc import *


class IkanmanSpider(scrapy.Spider):
    """
    classdocs

    example: http://www.ikanman.com/comic/11230/
    """
    dom = 'www.ikanman.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(IkanmanSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs['start_urls']
        self.root_path = kwargs['root_path']
        print(self.start_urls)

    title = ''

    def parse(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        episode_selectors = sel.xpath('//li/a[@class="status0"]')
        for episode_selector in episode_selectors:
            subtitle = episode_selector.xpath('@title').extract()[0]
            url = episode_selector.xpath('@href').extract()[0]
            url = response.urljoin(url)
            request = scrapy.Request(url, callback=self.parse_page_one)
            request.meta['title'] = '{0}/{1}'.format(title, subtitle)
            yield request

    def parse_page_one(self, response):
        title = response.meta['title']
        html = response.body.decode('utf-8')
        refUrl = response.url
        js = "var window = global;"

        """ emulate the javascript environment """
        rootDirPath = os.getcwd()
        """ Step one: analyze the ikanman_config.js """
        configPath = os.path.join(rootDirPath, "comicsCrawler/spiders/js/ikanman_config.js")
        with open(configPath, "rb") as f:
            configjs = f.read().decode('utf-8')
        # crypto = re.search(r"(var CryptoJS.+?)var pVars", configjs, re.S).group(1)
        js += re.search(
            r'^(var CryptoJS|window\["\\x65\\x76\\x61\\x6c"\]).+',
            configjs,
            re.MULTILINE
        ).group()
        js += re.search(
            r'<script type="text/javascript">((eval|window\["\\x65\\x76\\x61\\x6c"\]).+?)</script',
            html
        ).group(1)
        """ run javascript """
        ctx = execjs.compile(js)
        files, path = ctx.eval("[cInfo.files, cInfo.path]")

        """ Step two: analyze the ikanman_core.js"""
        corePath = os.path.join(rootDirPath, "comicsCrawler/spiders/js/ikanman_core.js")
        with open(corePath, "rb") as f:
            corejs = f.read().decode('utf-8')
            # cache server list
        servs = re.search(r"var servs=(.+?),pfuncs=", corejs).group(1)
        servs = execjs.eval(servs)
        servs = [host["h"] for category in servs for host in category["hosts"]]
        host = servs[0]
        utils = re.search(r"SMH\.(utils=.+?),SMH\.imgData=", corejs).group(1)
        js = utils + """;
            function getFiles(path, files, host) {
                // lets try if it will be faster in javascript
                return files.map(function(file){
                    return utils.getPath(host, path + file);
                });
            }
            """
        ctx = execjs.compile(js)
        urls = ctx.call("getFiles", path, files, host)

        for idx, url in enumerate(urls):
            img_name = "{0}/{1:03d}.jpg".format(title, idx+1)
            img_path = os.path.join(self.root_path, img_name)
            if os.path.isfile(img_path):
                continue
            item = ComicscrawlerItem()
            item['image_urls'] = [url]
            item['Referer'] = refUrl
            item['image_name'] = img_name
            yield item
