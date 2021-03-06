from imgdl import imgdl
from nose.tools import raises
import os
import hashlib
import tempfile

class TestCreateFolderName(object):
    def sub_title_and_key(self, title, album_key):
        return '{0} ({1})'.format(title, album_key)

    def test_no_change_to_valid_title(self):
        album_key = 'XbUFk'
        title_1 = 'A Valid title'
        name_1 = imgdl.create_folder_name(title_1, album_key)
        assert name_1 == self.sub_title_and_key(title_1, album_key)

        title_2 = 'a valid title 123'
        name_2 = imgdl.create_folder_name(title_2, album_key)
        assert name_2 == self.sub_title_and_key(title_2, album_key)

    def test_if_title_is_none_only_album_key(self):
        album_key = 'XbUFk'
        title = None
        name_1 = imgdl.create_folder_name(title, album_key)
        assert name_1 == 'XbUFk'

    def test_replace_exclamation_mark(self):
        album_key = 'XbUFk'
        title_1 = 'Test title!'
        name_1 = imgdl.create_folder_name(title_1, album_key)
        assert name_1 == self.sub_title_and_key('Test title', album_key)

    def test_replace_question_mark(self):
        album_key = 'XbUFk'
        title_1 = 'Test title?'
        name_1 = imgdl.create_folder_name(title_1, album_key)
        assert name_1 == self.sub_title_and_key('Test title', album_key)

class TestSourceUrl(object):
    def test_accept_imgur_urls(self):
        # does not raise exception
        imgdl.SourceUrl('http://imgur.com/a/B0s3o')

    @raises(imgdl.InvalidUrlError)
    def test_rejects_non_imgur_url(self):
        imgdl.SourceUrl('https://www.google.com/search')

    def test_extracts_album_key(self):
        assert imgdl.SourceUrl('http://imgur.com/a/B0s3o').album_key == 'B0s3o'

    def test_blog_url_format(self):
        blog_url = imgdl.SourceUrl('http://imgur.com/a/B0s3o').blog_url
        assert blog_url == 'https://imgur.com/a/B0s3o/layout/blog'


class TestAlbum(object):
    def test_extracts_album_title(self):
        source_url = imgdl.SourceUrl('http://imgur.com/gallery/nmHpn')
        album = imgdl.Album(source_url)
        title = album.album_title
        assert title == 'Lion gets best foot massage ever!'

    def test_counts_correct_number_of_images(self):
        source_url = imgdl.SourceUrl('http://imgur.com/a/B0s3o')
        album = imgdl.Album(source_url)
        assert album.num_images == 5

class TestDownloader(object):
    def hash_file(self, filename):
        with open(filename, 'rb') as fp:
            h = hashlib.new('md5')
            h.update(fp.read())
            return h.hexdigest()

    def test_downloads_jpegs(self):
        image_ids = ['ng7HmaP', 'tnnfEEj']
        image_fnames = ['0-ng7HmaP.jpg', '1-tnnfEEj.jpg']
        temp_dir = tempfile.TemporaryDirectory()

        downloader = imgdl.Downloader(image_ids, temp_dir.name)
        downloader.get_images()
        hash_1 = self.hash_file(os.path.join(temp_dir.name, image_fnames[0]))
        hash_2 = self.hash_file(os.path.join(temp_dir.name, image_fnames[1]))
        assert hash_1 == 'fc55e7da7b62216049d7ea63237efc03'
        assert hash_2 == 'c02dcc023bc7242f3221c01a0835942d'

    def test_downloads_webm(self):
        image_ids = ['BUVyEac']
        image_fnames = ['0-BUVyEac.webm']
        temp_dir = tempfile.TemporaryDirectory()

        downloader = imgdl.Downloader(image_ids, temp_dir.name)
        downloader.get_images()
        hash_1 = self.hash_file(os.path.join(temp_dir.name, image_fnames[0]))
        assert hash_1 == '728f074b099cfff721c755cf4d499765'
