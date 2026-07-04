from urllib.parse import parse_qs, urlparse

import pytest

from auth.services import AuthService
from core.settings import settings
from google_auth.services import GoogleAuthService

CLIENT_ID = 'test-client-id.apps.googleusercontent.com'


@pytest.fixture
def google_enabled(monkeypatch):
    monkeypatch.setattr(settings, 'GOOGLE_CLIENT_ID', CLIENT_ID)
    monkeypatch.setattr(settings, 'GOOGLE_CLIENT_SECRET', 'test-client-secret')


@pytest.fixture
def fake_claims(monkeypatch):
    claims = {
        'sub': 'google-sub-1',
        'email': 'user@example.com',
        'aud': CLIENT_ID,
        'iss': 'https://accounts.google.com',
    }

    async def fetch(self, code):
        return dict(claims)

    monkeypatch.setattr(GoogleAuthService, '_fetch_id_token_claims', fetch)
    return claims


def get_state(test_client) -> str:
    response = test_client.get('/auth/google/login', follow_redirects=False)
    assert response.status_code == 307, response.text
    location = response.headers['location']
    assert location.startswith('https://accounts.google.com/o/oauth2/v2/auth?')
    return parse_qs(urlparse(location).query)['state'][0]


def callback(test_client, state: str):
    return test_client.get(
        '/auth/google/callback', params={'code': 'test-code', 'state': state}, follow_redirects=False
    )


def login_username(test_client, refresh_token: str) -> str:
    response = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert response.status_code == 200, response.json()
    return AuthService.decode_access_token(response.json()['access_token']).username


def test_google_login_disabled_returns_404(test_client, monkeypatch):
    monkeypatch.setattr(settings, 'GOOGLE_CLIENT_ID', None)
    monkeypatch.setattr(settings, 'GOOGLE_CLIENT_SECRET', None)
    response = test_client.get('/auth/google/login', follow_redirects=False)
    assert response.status_code == 404, response.json()


def test_google_callback_creates_account(test_client, google_enabled, fake_claims):
    state = get_state(test_client)
    response = callback(test_client, state)
    assert response.status_code == 307, response.text
    assert response.headers['location'] == '/?oauth=ok'
    assert login_username(test_client, response.cookies['refresh_token']) == 'user@example.com'


def test_google_callback_reuses_account(test_client, google_enabled, fake_claims):
    first = callback(test_client, get_state(test_client))
    second = callback(test_client, get_state(test_client))
    assert login_username(test_client, first.cookies['refresh_token']) == 'user@example.com'
    assert login_username(test_client, second.cookies['refresh_token']) == 'user@example.com'


def test_google_callback_username_collision_falls_back_to_sub(test_client, google_enabled, fake_claims):
    test_client.post('/user/register', json={'username': 'user@example.com', 'password': 'pw'})
    response = callback(test_client, get_state(test_client))
    assert login_username(test_client, response.cookies['refresh_token']) == 'g_google-sub-1'


def test_google_callback_bad_state_redirects_to_error(test_client, google_enabled, fake_claims):
    response = callback(test_client, 'garbage')
    assert response.headers['location'] == '/?oauth=error'
    assert 'refresh_token' not in response.cookies


def test_google_callback_provider_error_redirects_to_error(test_client, google_enabled):
    response = test_client.get(
        '/auth/google/callback', params={'error': 'access_denied', 'state': 'x'}, follow_redirects=False
    )
    assert response.headers['location'] == '/?oauth=error'
