import pytest
from . import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


@pytest.fixture
def client():
    app = create_app(TestConfig)
    client = app.test_client()
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    return client
