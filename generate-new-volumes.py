#! python3
import os
import shutil

from scrapy.conf import settings


def save_episode_list(root):
    episode_list = generate_episode_list(root)
    index_file = settings['INDEX_FILE']
    index_path = os.path.join(root, index_file)
    with open(index_path, 'w') as f:
        for episode in episode_list:
            f.write(episode + '\n')


def generate_episode_list(root):
    episode_list = []
    for folder in os.listdir(root):
        folder_path = os.path.join(root, folder)
        if os.path.isdir(folder_path):
            episode_list.append(str(folder))
    episode_list.sort()
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


def generate_new_volume(root):
    episode_list = load_episode_list(root)
    volume_id = 1
    volume_page_threshold = 200
    volume_page = 1
    for episode in episode_list:
        print(episode)
        volume_name = 'volume{0}'.format(volume_id)
        volume_path = os.path.join(root, volume_name)
        if not os.path.isdir(volume_path):
            os.makedirs(volume_path)
        episode_path = os.path.join(root, episode)
        episode_pages = [page for page in os.listdir(episode_path)]
        episode_pages.sort()
        for idx, page in enumerate(episode_pages):
            src = os.path.join(episode_path, page)
            if os.path.isfile(src) and page[-4:] == '.jpg':
                dst = os.path.join(volume_path, '{0}.jpg'.format(volume_page + idx))
                shutil.copy(src, dst)
        volume_page += len(episode_pages)
        if volume_page > volume_page_threshold:
            volume_page = 1
            volume_id += 1


if __name__ == '__main__':
    root_dir = os.path.expanduser(settings['IMAGES_STORE'])
    root_dir = os.path.join(root_dir, '空中杀人鬼')
    save_episode_list(root_dir)
    input('Press any key after you finish editing: ')
    generate_new_volume(root_dir)
