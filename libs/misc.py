"""
Created on Dec 27, 2016

@author: yytang
"""
import contextlib
import json
import os
import re

import time


def get_spider_name_from_domain(dom):
    nameList = dom.split('.')
    prefix = ('' if len(nameList) == 2 or nameList[0] == 'www' else nameList[0])
    name = nameList[-2]
    suffix = ('' if nameList[-1] == 'com' else nameList[-1])
    spider_name = prefix + name + suffix
    return spider_name


def get_spider_name_from_url(url):
    dom = get_domain_from_url(url)
    return get_spider_name_from_domain(dom)


def get_domain_from_url(url):
    return re.search(r'http.?://([^\/]+)/', url).group(1)


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


def save_to_json(data, filePath):
    with open(filePath, 'w') as fd:
        json.dump(data, fd)


def load_from_json(filePath):
    if os.path.isfile(filePath):
        with open(filePath, 'r') as fd:
            data = json.load(fd)
    else:
        data = None
    return data


def polish_string(title, useless_ending='xxx'):
    """Return a safe directory name."""
    title = re.sub("《|》|~|[中文]|[Chinese]|【エロ漫画】", "", title).strip()
    title = re.sub("[/\\\?\|<>:\"\*]", " ", title).strip()
    title = re.sub('\s+', ' ', title).strip()
    title = re.sub(' \[\]', '', title).strip()
    # uselessEndings = [".txt", "txt", '全文阅读', '最新章节', useless_ending]
    #
    # for ending in uselessEndings:
    #     position = title.find(ending)
    #     position = position if position != -1 else len(title)
    #     # print('{0}-{1}-{2}'.format(ending, title, position))
    #     title = title[0:position]
    return title