#!/usr/bin/env python
# coding=utf-8
"""
Created on Dec 25, 2015

@author: yytang
"""
from itertools import cycle
from urllib.parse import urlencode

import execjs
import scrapy
from scrapy.selector import Selector

from comicsCrawler.items import ComicscrawlerItem
from libs.misc import *
from node_vm2 import VM, eval

class ManhuaguiSpider(scrapy.Spider):
    """
    classdocs

    example: https://www.manhuagui.com/comic/17965/
    """
    dom = 'www.manhuagui.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    custom_settings = {
        'DOWNLOAD_DELAY': 0.8,
    }

    def __init__(self, *args, **kwargs):
        super(ManhuaguiSpider, self).__init__(*args, **kwargs)
        self.root_path = kwargs['root_path']
        urls = kwargs['start_urls']
        self.start_urls = [self.polish_url(url) for url in urls]
        print(self.start_urls)

    def polish_url(self, url):
        url = url.strip('\n').strip()
        pattern = 'https?://www.manhuagui.com/comic/([\d]+)'
        url = re.search(pattern, url).group(0)
        return url

    def get_support_url(self, url):
        pattern = 'http://www.manhuagui.com/comic/([\d]+)'
        cid = re.search(pattern, url).group(1)
        support_url = 'http://www.manhuagui.com/support/chapters.aspx?id={0}'.format(cid)
        return support_url

    def save_subtitle_index(self, title, episode_list, index_name='original-index'):
        """ Saving the subtitle sequence into orginal-index file """
        comic_path = os.path.join(self.root_path, title)
        if not os.path.isdir(comic_path):
            os.mkdir(comic_path)
        index_path = os.path.join(comic_path, index_name)
        episode_list.reverse()
        with open(index_path, 'w') as f:
            for episode in episode_list:
                f.write(episode + '\n')

    def parse(self, response):
        episode_list = []
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        episode_selectors = sel.xpath('//li/a[@class="status0"]')
        for episode_selector in episode_selectors:
            subtitle = episode_selector.xpath('@title').extract()[0]
            episode_list.append(subtitle)
            url = episode_selector.xpath('@href').extract()[0]
            url = response.urljoin(url)
            request = scrapy.Request(url, callback=self.parse_page_one)
            request.meta['title'] = '{0}/{1}'.format(title, subtitle)
            yield request
        if not episode_selectors:
            support_url = self.get_support_url(response.url)
            request = scrapy.Request(support_url, callback=self.parse_support_page)
            request.meta['title'] = title
            yield request
        else:
            """ Saving the subtitle sequence into orginal-index file """
            self.save_subtitle_index(title, episode_list)

    def parse_support_page(self, response):
        title = response.meta['title']
        episode_list = []
        sel = Selector(response)
        episode_selectors = sel.xpath('//li/a[@class="status0"]')
        for episode_selector in episode_selectors:
            subtitle = episode_selector.xpath('@title').extract()[0]
            episode_list.append(subtitle)
            url = episode_selector.xpath('@href').extract()[0]
            url = response.urljoin(url)
            request = scrapy.Request(url, callback=self.parse_page_one)
            request.meta['title'] = '{0}/{1}'.format(title, subtitle)
            yield request
        self.save_subtitle_index(title, episode_list)

    def parse_page_one(self, response):
        title = response.meta['title']
        html = response.body.decode('utf-8')
        ref_url = response.url
        js = """
        	var window = global;
        	var cInfo;
        	var SMH = {
        		imgData: function(data) {
        			cInfo = data;
        			return {
        				preInit: function(){}
        			};
        		},
        	};
        	"""

        """ emulate the javascript environment """
        root_dir_path = os.getcwd()
        """ Step one: analyze the manhuagui_config.js """
        config_path = os.path.join(root_dir_path, "comicsCrawler/spiders/js/manhuagui_config.js")
        with open(config_path, "rb") as f:
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
        # ctx = execjs.compile(js)
        # files, path, md5, cid = ctx.eval("[cInfo.files, cInfo.path, cInfo.sl.md5, cInfo.cid]")
        with VM(js) as vm:
            files, path, md5, cid = vm.run("[cInfo.files, cInfo.path, cInfo.sl.md5, cInfo.cid]")

        """ Step two: analyze the manhuagui_core.js"""
        core_path = os.path.join(root_dir_path, "comicsCrawler/spiders/js/manhuagui_core.js")
        with open(core_path, "rb") as f:
            corejs = f.read().decode('utf-8')

        # # cache server list
        # servs = re.search(r"var servs=(.+?),pfuncs=", corejs).group(1)
        # servs = eval(servs)
        # servs = [host["h"] for category in servs for host in category["hosts"]]
        #
        # global servers
        # servers = cycle(servs)
        #
        # host = next(servers)
        host = 'us'
        utils = re.search(r"SMH\.(utils=.+?),SMH\.imgData=", corejs).group(1)
        # js = utils + """;
        #     function getFiles(path, files, host) {
        #         // lets try if it will be faster in javascript
        #         return files.map(function(file){
        #             return utils.getPath(host, path + file);
        #         });
        #     }
        #     """
        js = """        
            var location = {
                protocol: "http:"
            };
            """ + utils + """;
            function getFiles(path, files, host) {
                // lets try if it will be faster in javascript
                return files.map(function(file){
                    return utils.getPath(host, path + file);
                });
            }        
        """
        # ctx = execjs.compile(js)
        # urls = ctx.call("getFiles", path, files, host)
        with VM(js) as vm:
            urls = vm.call("getFiles", path, files, host)

        params = urlencode({
            "cid": cid,
            "md5": md5
        })
        urls = ['{url}?{params}'.format(url=url, params=params) for url in urls]

        for idx, url in enumerate(urls):
            img_name = "{0}/{1:03d}.jpg".format(title, idx + 1)
            img_path = os.path.join(self.root_path, img_name)
            if os.path.isfile(img_path):
                continue
            item = ComicscrawlerItem()
            item['image_urls'] = [url]
            item['Referer'] = ref_url
            item['image_name'] = img_name
            yield item
