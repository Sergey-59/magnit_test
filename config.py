import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_for-MAGNIT'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # отладчик
    FLASK_SKIP_DOTENV = 0
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG') or 0
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret'
    # mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['s.pertak@gmail.com']
    # CELERY RABBIT
    CELERY_BROKER_URL = os.environ.get('RABBITMQ')
    BEAT_SCHEDULE = {
        'check_auction': {
            'task': 'tasks.check_auction',
            'schedule': 60.0,
            'args': ()
        }
    }

