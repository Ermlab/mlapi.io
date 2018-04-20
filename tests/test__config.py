# tests/test_config.py


import unittest

from flask import current_app
from flask_testing import TestCase

from mlapi.app import app
from db import config

class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('db.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///mlapi_db.db'
        )

class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('db.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///mlapi_db_tests.db'
        )

if __name__ == '__main__':
    unittest.main()
