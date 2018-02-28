import os
import logging

logger = logging.getLogger(__name__)

APP_MODE_DEV = 'DEV'
APP_MODE_PROD = 'PROD'


class Config(object):
    DEBUG = False
    APP_MODE = APP_MODE_DEV
    TESTING = False
    SENTRY_DSN = None


class ProductionConfig(Config):
    APP_MODE = APP_MODE_PROD
    try:
        DATABASE_URI = os.environ['DATABASE_URI']
    except KeyError:
        DATABASE_URI = None
        logger.warn("No DATABASE_URI in your environment!")
    try:
        SENTRY_DSN = os.environ['SENTRY_DSN']
    except KeyError:
        SENTRY_DSN = None
        logger.warn("No SENTRY_DSN in your environment!")
    ECHO = False


class DevelopmentConfig(Config):
    DEBUG = True
    ECHO = False
    DATABASE_URI = 'sqlite:///:memory:'


def is_prod_mode():
    try:
        return os.environ['APP_MODE'] == APP_MODE_PROD
    except KeyError:
        return False
