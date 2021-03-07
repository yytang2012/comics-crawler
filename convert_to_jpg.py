import os

import cv2


def get_all_files(dir_path, file_extension='.avi$.mp4$.kvm', depth=50, ignore_dir='finished$completed'):
    root_path = os.path.expanduser(dir_path)
    file_extension_tuple = tuple(file_extension.split('$'))
    if os.path.isfile(root_path) is True:
        return [root_path] if root_path.endswith(file_extension_tuple) else []
    else:
        results = get_files(root_path=root_path, depth=depth, file_extension=file_extension, ignore_dir=ignore_dir)
        return results


def get_files(root_path, depth=50, file_extension='.avi$.mp4$.kvm', ignore_dir='finished$completed'):
    file_extension_tuple = tuple(file_extension.split('$'))
    ignore_dir_tuple = tuple(ignore_dir.split('$'))
    res = []
    for file in os.listdir(root_path):
        if file in ignore_dir_tuple:
            continue
        file_path = os.path.join(root_path, file)
        if os.path.isfile(file_path) is True:
            if file_path.endswith(file_extension_tuple) is True:
                res.append(file_path)
        elif depth > 0:
            res += get_files(file_path, depth - 1, file_extension=file_extension, ignore_dir=ignore_dir)
        else:
            pass
    return res


def convert_image_format(image_dir, file_extention='.jpg'):
    all_image_path = get_all_files(image_dir, file_extension='.webp')
    for image_path in all_image_path:
        base, _ = image_path.split('.')
        frame = cv2.imread(image_path)
        new_image_path = base + file_extention
        cv2.imwrite(new_image_path, frame)
        os.remove(image_path)


if __name__ == '__main__':
    image_dir = "/home/yytang/comiccrawler/download/"
    convert_image_format(image_dir)
