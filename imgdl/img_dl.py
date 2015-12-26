#!/usr/bin/env python3

import argparse
import os
import re
import urllib.request
import urllib.parse


class SourceUrl(object):
    def __init__(self, url_string):
        self.user_url = url_string
        self._url_parts = urllib.parse.urlparse(url_string)
        self.album_key = self._parse_key()

    def _parse_key(self):
        result = re.search(r'\/([a-zA-Z0-9]*)$', self._url_parts.path)
        return result.group(1)

    def is_imgur(self):
        match = re.search(r'imgur\.com', self._url_parts.netloc)
        if match:
            return True
        return False

    @property
    def blog_url(self):
        return 'https://imgur.com/a/' + self.album_key + '/layout/blog'


class Album(object):
    def __init__(self, source_url):
        self.url = source_url
        self.image_ids = self._extract_img_ids()

    def _extract_img_ids(self):
        raw_html = self._get_blog_page()
        img_url_re = r'<div\sid="([a-zA-Z0-9]*)"\sclass=".*post-image-container.*">'
        return re.findall(img_url_re, raw_html)

    def _get_blog_page(self):
        return self._get_page(self.url.user_url)

    def _get_user_page(self):
        return self._get_page(self.url.blog_url)

    def _get_page(self, url):
        print('Downloading HTML from {}'.format(url))
        response = urllib.request.urlopen(url)
        raw_bytes = response.read()
        return raw_bytes.decode('utf-8')

    @property
    def album_title(self):
        raw_html = self._get_user_page()
        with open('temp.html', 'w') as f:
            f.write(raw_html)
        title_re = r'<title>\s*(.*) - Album on Imgur<\/title>'
        match = re.search(title_re, raw_html)
        if match:
            return match.group(1).strip()
        return None

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

    def _request_image_header(self, image_id):
        url = urllib.parse.urljoin(self.root, image_id + '.jpg')
        request = urllib.request.Request(url, method='HEAD')
        response = urllib.request.urlopen(request)
        return response

    def _file_extension_from_header(self, headers):
        content_type = headers['Content-type'].lower()
        if 'jpeg' in content_type:
            file_extension = 'jpg'
        elif 'webm' in content_type:
            file_extension = 'webm'
        elif 'gif' in content_type:
            file_extension = 'gif'
        elif 'png' in content_type:
            file_extension = 'png'
        else:
            file_extension = 'dat'
        return file_extension

    def get_images(self):
        total = len(self.image_ids)
        digits = len(str(total))
        base_filename = ('{index:0' + str(digits) +
                         'd}-{image_id:s}.{file_extension}')

        for num, image_id in enumerate(self.image_ids):
            print('File {0}/{1}...'.format(num+1, total),
                  end="",
                  flush=True)
            header_resp = self._request_image_header(image_id)
            file_extension = self._file_extension_from_header(
                header_resp.headers)
            filename = base_filename.format(
                index=num,
                image_id=image_id,
                file_extension=file_extension
                )
            filepath = os.path.join(self.directory, filename)
            if os.path.exists(filepath):
                print('{0} already exists. Skipping.'.format(
                    filename))
                continue
            url = urllib.parse.urljoin(self.root, image_id)
            response = urllib.request.urlopen(url + '.' + file_extension)
            with open(filepath, 'wb') as fp:
                fp.write(response.read())
            print('done.')


def create_folder_name(title, album_key):
    # only allow alphanumerics, space, dash, underscore, apostrophe
    # replace everything else with space and strip whitespace
    if title:
        subbed = re.sub(r'[^a-zA-Z0-9_\'\-\s]', ' ', title).strip()
        with_key = subbed + ' (' + album_key + ')'
        return with_key
    else:
        return album_key


def main(url, dest_folder):
    source_url = SourceUrl(url)
    album = Album(source_url)

    print('{0} ({1}): {2} images'.format(
        album.album_title,
        source_url.album_key,
        album.num_images))

    if dest_folder:
        directory = dest_folder
    else:
        directory = create_folder_name(
            album.album_title,
            source_url.album_key)

    downloader = Downloader(album.image_ids, directory)
    downloader.get_images()
    exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='img-dl, a command line utility for downlading web albums')
    parser.add_argument('URL', help='Imgur album URL')
    parser.add_argument('PATH', help='Download images into this folder', nargs='?')
    args = parser.parse_args()
    main(args.URL, args.PATH)
