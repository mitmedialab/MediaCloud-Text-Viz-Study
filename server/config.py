import os

class Config(object):
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DATABASE_URI = os.environ['DATABASE_URI']
    ECHO = False

class DevelopmentConfig(Config):
    DEBUG = True
    ECHO = False
    DATABASE_URI = 'sqlite:///:memory:'
