class Config(object):
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    ECHO = False

class DevelopmentConfig(Config):
    DEBUG = True
    ECHO = False
    DATABASE_URI = 'sqlite:///:memory:'
