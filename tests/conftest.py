import pytest
from app import create_app
from app.models import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Roll back DB after every test to keep tests isolated."""
    with app.app_context():
        yield
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


def register_user(client, username='trader', email='trader@test.com', password='password123'):
    return client.post('/auth/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password,
    }, follow_redirects=True)


def login_user(client, email='trader@test.com', password='password123'):
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)
