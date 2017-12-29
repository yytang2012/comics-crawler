from collections import defaultdict

from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from libs.misc import *
from libs.urlcheck import url_check


class ComicsCrawler:
    crawler_process = CrawlerProcess(get_project_settings())

    def __init__(self):
        root_path = settings['ROOT_PATH']
        if not os.path.isdir(root_path):
            os.makedirs(root_path)
        self._start_urls = defaultdict(lambda: [])
        self.url_path = settings['URL_PATH']
        self.image_download_path = settings['IMAGES_STORE']
        self.allowed_domains = self.get_allowed_domains(True)

    def get_allowed_domains(self, write_to_file=False):
        allowed_domains = []
        for spider_name in self.crawler_process.spiders.list():
            spider = self.crawler_process.spiders.load(spider_name)
            try:
                allowed_domains += spider.allowed_domains
            except Exception:
                print("{0}: allowed domain is not defined".format(spider_name))
        allowed_domains.sort()
        if write_to_file:
            with open('allowed_domains.dat', 'w') as f:
                for url in allowed_domains:
                    f.write('{0}\n'.format(url))
        return allowed_domains

    def start_url_init(self, urls=None):
        if not urls:
            with open(self.url_path, 'r') as f:
                urls = f.readlines()
        # 1. Remove the spaces
        # 2. Convert the urls to supported format
        # 3. Remove the urls not supported
        urls = [url.strip() for url in urls if len(url.strip()) != 0]
        urls = [url_check(url) for url in urls]
        urls = [url for url in urls if get_domain_from_url(url) in self.allowed_domains]

        for url in urls:
            spider_name = get_spider_name_from_url(url)
            self._start_urls[spider_name].append(url)

    def start_downloading(self):
        for spider_name, start_urls in self._start_urls.items():
            self.crawler_process.crawl(spider_name, start_urls=start_urls, root_path=self.image_download_path)
        self.crawler_process.start()


def main(urls=None):
    with stopwatch('Main'):
        crawler = ComicsCrawler()
        crawler.start_url_init(urls)
        crawler.start_downloading()


if __name__ == '__main__':
    main()
