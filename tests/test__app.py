import os
import unittest
import json
import base64
from flask import Flask, jsonify
from flask_testing import TestCase
from flask_jwt import jwt_required, current_identity
from mlapi.app import app, image_storage, database, jwt
from db.dbModels import User
from unittest.mock import mock_open, call
try:
    import mock
except ImportError:
    from unittest import mock

def jwt_mock(self, fn):
    def wrapper(fn, *args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

class TestApp(TestCase):

    TESTING = True

    def create_app(self):
        app.config.from_object('db.config.TestingConfig')
        database.drop_all()
        database.create_all()
        test_user = User("test","test")
        database.session.add(test_user)
        database.session.commit()
        self.image_storage = image_storage
        return app
    
    
    ############################################################
    ####################### AUTH TESTS #########################
    ############################################################
    def test_getting_token(self):
        response = self.client.post("/auth",
            data='{"username":"test", "password":"test"}',
            headers={'content-type': 'application/json'}
        )
        self.assert_200(response)

    def test_authorization_while_providing_valid_token(self):
        get_token = self.client.post("/auth",
            data='{"username":"test", "password":"test"}',
            headers={'content-type': 'application/json'}
        )
        token = get_token.json['access_token']
        response = self.client.get(
            "/v2/token",
            headers={"Authorization": "JWT " + token}
        )
        self.assert200(response)

    def test_not_getting_token_providing_wrong_credentails(self):
        response = self.client.post("/auth",
            data='{"username":"test", "password":"test1"}',
            headers={'content-type': 'application/json'}
        )
        self.assert401(response)

    def test_not_getting_token_providing_no_credentails(self):
        response = self.client.post("/auth",
            data='{}',
            headers={'content-type': 'application/json'}
        )
        self.assert401(response)
    
    ############################################################
    ######################## GET TESTS #########################
    ############################################################
    @mock.patch("flask_jwt._jwt_required")
    def test_app_is_responding_on_get_cars(self, monkeypatch):
        monkeypatch = jwt_mock
        response = self.client.get("/v2/cars")
        valid_response = {
                "description" : "Make an authenticated POST request for predicting the image. POST binary file with proper header or { 'image' : 'BASE64 image' }",
                "accepted_content_type" : [
                    "image/jpeg",
                    "image/png",
                    "application/json"
                ]
            }
        self.assertEquals(response.json, valid_response)

    @mock.patch("flask_jwt._jwt_required")
    def test_app_is_responding_on_get_sentiment(self, monkeypatch):
        monkeypatch = jwt_mock
        response = self.client.get("/v2/sentiment")
        valid_response = {
                "description" : "Make an authenticated POST request for predicting the text. { 'text' : 'Text to predict' }",
                "accepted_content_type" : [
                    "application/json"
                ]
            }
        self.assertEquals(response.json, valid_response)

    @mock.patch("flask_jwt._jwt_required")
    def test_app_is_responding_on_get_root(self, monkeypatch):
        monkeypatch = jwt_mock
        response = self.client.get("/v2/")
        valid_response = {
            'available_routes': [ 
                "api.mlapi.io/v2/token - Check current token balance status [POST]",
                "api.mlapi.io/v2/cars - Car recognition NN[GET, POST]",
                "api.mlapi.io/v2/sentiment - Text Sentiment Analysis [GET, POST]",
                ]
        }
        self.assertEquals(response.json, valid_response)
        
    @mock.patch("flask_jwt._jwt_required")
    @mock.patch("flask_jwt.current_identity")
    def test_app_is_redirecting_from_slash(self, identity_mock, monkeypatch):
        monkeypatch = jwt_mock
        identity_mock = { 'user_id' : 1 }

        response = self.client.get("/")
        self.assertRedirects(response, '/v2/')
    # @mock.patch("flask_jwt._jwt_required")
    # @mock.patch("flask_jwt.current_identity")
    # def test_app_is_redirecting_from_get_cars_with_trailing_slash(self, identity_mock, monkeypatch):
    #     monkeypatch = jwt_mock
    #     identity_mock = { 'user_id' : 1 }

    #     response = self.client.get("/v2/cars/")
    #     self.assertRedirects(response, '/v2/cars')

    # @mock.patch("flask_jwt._jwt_required")  
    # @mock.patch("flask_jwt.current_identity")
    # def test_app_is_redirecting_from_get_sentiment_with_trailing_slash(self, identity_mock, monkeypatch):
    #     monkeypatch = jwt_mock
    #     identity_mock = { 'user_id' : 1 }

    #     response = self.client.get("/v2/sentiment/")
    #     self.assertRedirects(response, '/v2/sentiment')

    ############################################################
    ######################## POST TESTS ########################
    ############################################################
    @mock.patch("flask_jwt._jwt_required")
    @mock.patch("flask_jwt.current_identity")
    def test_app_is_responding_on_post_sentiment(self, identity_mock, monkeypatch):
        monkeypatch = jwt_mock
        identity_mock = { 'user_id' : 1 }

        response = self.client.post("/v2/sentiment",
            data='{"text":"polecam"}',
            headers={'content-type': 'application/json'}
        )
        valid_response = "{'prediction': ['Neutral: 0.11%', 'Positive: 99.52%', 'Negative: 0.34%']}".split(":")[1::2]
        self.assert_200(response, "Not returned 200 code.")
        self.assertEquals(str(response.json).split(":")[1::2], valid_response)

    @mock.patch("flask_jwt._jwt_required")
    @mock.patch("flask_jwt.current_identity")
    @mock.patch.object(image_storage,"_uuidgen")
    def test_posted_binary_image_gets_saved(self, patch_uuid, identity_mock, patch_jwt):
        identity_mock = { 'user_id' : 1 }
        file_save_prefix = "./images/"
        fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
        patch_jwt = jwt_mock
        patch_uuid.return_value = fake_uuid
       

        # When the service receives an image through POST...
        fake_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x01\x08\x02\x00\x00\x00{@\xe8\xdd\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe2\x01\x19\x0c(\x03Jg'\xf8\x00\x00\x00\x0fIDAT\x08\xd7c\x9c?\xbd\xe5\xfd'F\x00\r}\x03\x9e\x7f\xa9T\xcc\x00\x00\x00\x00IEND\xaeB`\x82"
        
        image_name = "{}.{}".format(fake_uuid, "jpg")
        response = self.client.post(
            '/v2/cars',
            data=fake_image_bytes,
            headers={'content-type': 'image/jpeg'}
        )
        self.assert_200(response, "Not returned 200 code. Failed to save jpeg image.")
        
        file_path = file_save_prefix + image_name
        with open(file_path, 'rb') as image_file:
            self.assertEquals(image_file.read(),fake_image_bytes)
        os.remove(file_path)

        image_name = "{}.{}".format(fake_uuid, "png")
        response = self.client.post(
            '/v2/cars',
            data=fake_image_bytes,
            headers={'content-type': 'image/png'}
        )
        self.assert_200(response, "Not returned 200 code. Failed to save png image.")

        file_path = file_save_prefix + image_name
        with open(file_path, 'rb') as image_file:
            self.assertEquals(image_file.read(),fake_image_bytes)
        os.remove(file_path)
    
    @mock.patch("flask_jwt._jwt_required")
    @mock.patch("flask_jwt.current_identity")
    @mock.patch.object(image_storage,"_uuidgen")
    def test_posted_base64_image_gets_saved(self, patch_uuid, identity_mock, patch_jwt):
    
        identity_mock = { 'user_id' : 1 }
        file_save_prefix = "./images/"
        fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
        patch_jwt = jwt_mock
        patch_uuid.return_value = fake_uuid
       
        # When the service receives an image through POST...
        fake_image_json = {'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAIAAAB7QOjdAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4gEZDCgDSmcn+AAAAA9JREFUCNdjnD+95f0nRgANfQOef6lUzAAAAABJRU5ErkJggg=='}
        b = base64.b64decode(fake_image_json['image'].split(",")[1])
        image_name = "{}.{}".format(fake_uuid, "png")
        response = self.client.post(
            '/v2/cars',
            data=json.dumps(fake_image_json),
            headers={'content-type': 'application/json'}
        )
        self.assert_200(response, "Not returned 200 code. Failed to save Base64 png image.")
        
        file_path = file_save_prefix + image_name
        with open(file_path, 'rb') as image_file:
            self.assertEquals(image_file.read(), b)
        os.remove(file_path)

if __name__ == '__main__':
    unittest.main()