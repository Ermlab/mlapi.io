import os
import unittest
import json
from io import BytesIO
from mlapi.images import ImageStorage
from unittest import mock, TestCase

#TODO:true unittest ImageStorage, przypadki brzegowe
class MyTest(TestCase):
    TESTING = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
        self.image_storage = ImageStorage("./images", uuidgen=lambda: fake_uuid)

    def test_image_gets_saved(self):
        fake_image_bytes = b"1\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x01\x08\x02\x00\x00\x00{@\xe8\xdd\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe2\x01\x19\x0c(\x03Jg'\xf8\x00\x00\x00\x0fIDAT\x08\xd7c\x9c?\xbd\xe5\xfd'F\x00\r}\x03\x9e\x7f\xa9T\xcc\x00\x00\x00\x00IEND\xaeB`\x82"
        a = BytesIO(fake_image_bytes)
        image_name = self.image_storage.save(a, "image/png")
        
        with open(image_name, 'rb') as image_file:
            assert image_file.read() == fake_image_bytes
        os.remove(image_name)