#! python3
import os
import shutil

import re
from scrapy.conf import settings


def save_episode_list(root, comic_name):
    root_dir = os.path.join(root, comic_name)
    episode_list = generate_episode_list(root_dir)
    index_file = settings['INDEX_FILE']
    index_path = os.path.join(root_dir, index_file)
    with open(index_path, 'w') as f:
        for episode in episode_list:
            f.write(episode + '\n')


def generate_episode_list(root):
    episode_list = []
    for folder in os.listdir(root):
        folder_path = os.path.join(root, folder)
        if os.path.isdir(folder_path):
            episode_list.append(str(folder))

    def sort_func(s):
        p = '[^\d]+([\d]+)'
        m = re.search(p, s)
        if m is None:
            return 0
        else:
            return int(m.group(1))

    episode_list.sort(key=lambda v: sort_func(v))
    print(str(episode_list))
    return episode_list


def load_episode_list(root):
    index_file = settings['INDEX_FILE']
    index_path = os.path.join(root, index_file)
    episode_list = []
    with open(index_path, 'r') as f:
        for episode in f.readlines():
            episode_list.append(episode.strip())
            print(episode)
    return episode_list


def generate_new_volume(root, comic_name):
    comic_path = os.path.join(root, comic_name)
    episode_list = load_episode_list(comic_path)
    volume_id = 1
    volume_page_threshold = 200
    volume_page = 1
    new_comic_name = comic_name + '-volumes'
    new_comic_path = os.path.join(root, new_comic_name)
    if not os.path.isdir(new_comic_path):
        os.makedirs(new_comic_path)

    for episode in episode_list:
        print(episode)
        volume_name = 'volume{0}'.format(volume_id)
        volume_path = os.path.join(new_comic_path, volume_name)
        if not os.path.isdir(volume_path):
            os.makedirs(volume_path)
        episode_path = os.path.join(comic_path, episode)
        episode_pages = [page for page in os.listdir(episode_path)]
        episode_pages.sort()
        for idx, page in enumerate(episode_pages):
            src = os.path.join(episode_path, page)
            if os.path.isfile(src) and page[-4:] == '.jpg':
                dst = os.path.join(volume_path, '{0:03d}.jpg'.format(volume_page + idx))
                shutil.copy(src, dst)
        volume_page += len(episode_pages)
        if volume_page > volume_page_threshold:
            volume_page = 1
            volume_id += 1


if __name__ == '__main__':
    comic_name = '一拳超人'
    root_dir = os.path.expanduser(settings['IMAGES_STORE'])
    save_episode_list(root_dir, comic_name)
    input('Press any key after you finish editing: ')
    generate_new_volume(root_dir, comic_name)
