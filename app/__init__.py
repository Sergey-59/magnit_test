import logging
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from flask_mail import Mail
from config import Config
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_jwt_extended import JWTManager
from flask_apispec.extension import FlaskApiSpec
from logging.handlers import SMTPHandler


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
docs = FlaskApiSpec()
mail = Mail()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
celery.conf.beat_schedule = Config.BEAT_SCHEDULE


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='magnit_test',
            version='v1',
            openapi_version='2.0',
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/'
    })

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    docs.init_app(app)
    mail.init_app(app)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='MAGNIT-TEST Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return app
