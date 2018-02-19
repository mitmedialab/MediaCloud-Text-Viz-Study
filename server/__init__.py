import os
import sys
import logging.config
import json
import datetime
from flask import Flask, render_template, jsonify, request

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# just log to stdout so it works well on prod containers
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# TODO: deal with log levels...?
logger = logging.getLogger(__name__)
logger.info('---------------------------------------------------------------------------')
logger.info('Starting web app')


def create_app():
    app = Flask(__name__)
    app.config.from_object('server.config.DevelopmentConfig')
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
