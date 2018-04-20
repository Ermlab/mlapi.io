# API/tests/base.py


from flask_testing import TestCase

from mlapi.app import app, db
from db import config


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('db.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
