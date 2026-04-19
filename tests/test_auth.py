import pytest
from tests.conftest import register_user, login_user


class TestRegistration:

    def test_register_success(self, client):
        response = register_user(client)
        assert response.status_code == 200
        assert b'Welcome' in response.data or b'Dashboard' in response.data

    def test_register_duplicate_email(self, client):
        register_user(client)
        response = register_user(client, username='trader2')
        assert b'already exists' in response.data

    def test_register_duplicate_username(self, client):
        register_user(client)
        response = register_user(client, email='other@test.com')
        assert b'already taken' in response.data

    def test_register_password_mismatch(self, client):
        response = client.post('/auth/register', data={
            'username': 'trader',
            'email': 'trader@test.com',
            'password': 'password123',
            'confirm_password': 'different',
        }, follow_redirects=True)
        assert b'must match' in response.data

    def test_register_short_password(self, client):
        response = client.post('/auth/register', data={
            'username': 'trader',
            'email': 'trader@test.com',
            'password': 'short',
            'confirm_password': 'short',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' not in response.data


class TestLogin:

    def test_login_success(self, client):
        register_user(client)
        client.get('/auth/logout')
        response = login_user(client)
        assert response.status_code == 200
        assert b'Welcome back' in response.data

    def test_login_wrong_password(self, client):
        register_user(client)
        client.get('/auth/logout')
        response = client.post('/auth/login', data={
            'email': 'trader@test.com',
            'password': 'wrongpassword',
        }, follow_redirects=True)
        assert b'Invalid' in response.data

    def test_login_wrong_email(self, client):
        response = client.post('/auth/login', data={
            'email': 'nobody@test.com',
            'password': 'password123',
        }, follow_redirects=True)
        assert b'Invalid' in response.data

    def test_logout(self, client):
        register_user(client)
        response = client.get('/auth/logout', follow_redirects=True)
        assert b'logged out' in response.data

    def test_protected_redirects_when_unauthenticated(self, client):
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']
