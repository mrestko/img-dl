#!/usr/bin/env python3

import argparse
import os
import re
import urllib.request
import urllib.parse


class SourceUrl(object):
    def __init__(self, url_string):
        self.url_parts = urllib.parse.urlparse(url_string)
        self.album_key = self._parse_key()

    def _parse_key(self):
        result = re.search(r'\/([a-zA-Z0-9]*)$', self.url_parts.path)
        return result.group(1)

    def is_imgur(self):
        match = re.search(r'imgur\.com', self.url_parts.netloc)
        if match:
            return True
        return False

    @property
    def blog_url(self):
        return 'https://imgur.com/a/' + self.album_key + '/layout/blog'


class Album(object):
    def __init__(self, album_url):
        self.url = album_url
        self.page_html = self._get_page()
        self.image_ids = self._extract_img_ids()

    def _extract_img_ids(self):
        img_url_re = r'<div\sid="([a-zA-Z0-9]*)"\sclass=".*post-image-container.*">'
        return re.findall(img_url_re, self.page_html)

    def _get_page(self):
        response = urllib.request.urlopen(self.url)
        raw_bytes = response.read()
        return raw_bytes.decode('utf-8')

    @property
    def album_title(self):
        title_re = r'<title>\s*(.*) - Album on Imgur<\/title>'
        match = re.search(title_re, self.page_html)
        return match.group(1).strip()

    @property
    def num_images(self):
        return len(self.image_ids)


class Downloader(object):
    def __init__(self, image_ids, directory):
        self.root = 'https://i.imgur.com'
        self.image_ids = image_ids
        self.directory = self._directory(directory)

    def _directory(self, directory):
        norm_dir = os.path.normpath(directory)
        if not os.path.exists(norm_dir):
            os.makedirs(norm_dir)
        return norm_dir

    def get_images(self):
        for image_id in self.image_ids:
            url = urllib.parse.urljoin(self.root, image_id)
            # if we don't specify a filetype, then imgur may redirect to
            # a webpage. We'll lie and say we want jpg then figure out what
            # kind of file we actually get
            response = urllib.request.urlopen(url + '.jpg')
            file_type = response.headers['Content-type'].lower()
            if 'jpeg' in file_type:
                file_extension = 'jpg'
            elif 'webm' in file_type:
                file_extension = 'webm'
            elif 'gif' in file_type:
                file_extension = 'gif'
            elif 'png' in file_type:
                file_extension = 'png'
            else:
                file_extension = 'dat'
            filename = os.path.join(self.directory, image_id + '.' + file_extension)
            with open(filename, 'wb') as fp:
                fp.write(response.read())


def sanitize_title_for_path(title):
    # only allow alphanumerics, space, dash, underscore, apostrophe
    # replace everything else with space and strip whitespace
    subbed = re.sub(r'[^a-zA-Z0-9_\'\-\s]', ' ', title)
    return subbed.strip()


def main():
    parser = argparse.ArgumentParser(
        description='img-dl, a command line utility for downlading web albums')
    parser.add_argument('URL', help='Imgur album URL')
    parser.add_argument('PATH', help='Download images into this folder', nargs='?')
    args = parser.parse_args()

    source_url = SourceUrl(args.URL)
    album = Album(source_url.blog_url)

    print('{0} ({1}): {2} images'.format(
        album.album_title,
        source_url.album_key,
        album.num_images))

    if args.PATH:
        directory = args.PATH
    else:
        directory = sanitize_title_for_path(album.album_title)

    downloader = Downloader(album.image_ids, directory)
    downloader.get_images()
    exit()

if __name__ == '__main__':
    main()
