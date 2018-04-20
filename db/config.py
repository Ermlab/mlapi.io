# db/config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite3_local_base = 'sqlite:///'
database_name = 'mlapi_db'


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('DB_SECRET_KEY')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = sqlite3_local_base + database_name + '.db'

class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    DISABLE_JWT = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = sqlite3_local_base + database_name + '_tests.db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////data/DB/mlapi_db.db'
