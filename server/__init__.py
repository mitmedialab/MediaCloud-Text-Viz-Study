import os
import sys
import logging.config
from flask import Flask
from raven.conf import setup_logging
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import is_prod_mode

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# just log to stdout so it works well on prod containers
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# TODO: deal with log levels...?
logger = logging.getLogger(__name__)
logger.info('---------------------------------------------------------------------------')
logger.info('Starting web app')


def create_app():
    app = Flask(__name__)
    if config.is_prod_mode():
        app.config.from_object('server.config.ProductionConfig')
    else:
        app.config.from_object('server.config.DevelopmentConfig')
    # Set up sentry logging
    if app.config['SENTRY_DSN'] is not None:
        handler = SentryHandler(app.config['SENTRY_DSN'])
        handler.setLevel(logging.ERROR)
        setup_logging(handler)
        Sentry(app, dsn=app.config['SENTRY_DSN'])
        logger.info('Logging to Sentry')
    else:
        logger.info('No Sentry logging')
    return app


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from server.models.user import User, Response
    Base.metadata.create_all(bind=engine)

# Set up app and database
app = create_app()

# REFERENCE: http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/
engine = create_engine(app.config['DATABASE_URI'], convert_unicode=True, echo=app.config['ECHO'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
init_db()
logger.info('---- Database initialized ----')


# TODO: not sure if this should go here or in survey.py
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


import server.views.survey
