# encoding=utf-8
import os
import random

from scrapy.conf import settings
from libs.user_agents import agents


class UserAgentMiddleware(object):
    """ Randomly choose a User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class ProxyDownloaderMiddleware(object):
    def __init__(self):
        # proxy_path = os.path.expanduser(settings['PROXY_FILE'])
        self.proxy_pool = [
            ("68.183.62.255", "8080"),
            ("205.201.204.65", "46220"),
            ("216.80.32.98", "8082"),
            ("47.254.44.16", "8080"),
            ("45.32.164.224", "3128"),
            ("35.186.186.238", "80"),
            ("151.80.108.134", "3128"),
            ("201.77.166.247", "8081"),
            ("107.170.237.191", "8080"),
            ("92.222.237.94", "8898"),

        ]

    def process_request(self, request, spider):
        if len(self.proxy_pool) != 0:
            proxy = random.choice(self.proxy_pool)
            request.meta['proxy'] = 'http://{0}:{1}'.format(proxy[0], proxy[1])
            print(request.meta['proxy'])
