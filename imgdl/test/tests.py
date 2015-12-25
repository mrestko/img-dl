import pytest

from img_dl import imgdl

class TestCreateFolderName(object):
    def sub_title_and_key(self, title, album_key):
        return '{0} ({1})'.format(title, album_key)

    def test_no_change_to_valid_title(self):
        album_key = 'XbUFk'
        title_1 = 'A Valid title'
        name_1 = img_dl.create_folder_name(title_1, album_key)
        assert name_1 == self.sub_title_and_key(title_1, album_key)

        title_2 = 'a valid title 123'
        name_2 = img_dl.create_folder_name(title_2, album_key)
        assert name_2 == self.sub_title_and_key(title_2, album_key)

    def test_if_title_is_none_only_album_key(self):
        album_key = 'XbUFk'
        title = None
        name_1 = img_dl.create_folder_name(title, album_key)
        assert '(XbUFk)' == name_1
