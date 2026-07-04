import hashlib
import hmac
import time

import pytest

from auth.services import AuthService
from core.settings import settings

TEST_BOT_TOKEN = '12345:TEST_TOKEN'


def make_widget_params(telegram_id=123456, bot_token=TEST_BOT_TOKEN, auth_date=None, **extra):
    data = {
        'id': str(telegram_id),
        'first_name': 'Test',
        'auth_date': str(auth_date if auth_date is not None else int(time.time())),
        **extra,
    }
    check_string = '\n'.join(f'{key}={data[key]}' for key in sorted(data))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    data['hash'] = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return data


@pytest.fixture
def bot_token(monkeypatch):
    monkeypatch.setattr(settings, 'BOT_TOKEN', TEST_BOT_TOKEN)
    return TEST_BOT_TOKEN


def login_username(test_client, refresh_token: str) -> str:
    response = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert response.status_code == 200, response.json()
    return AuthService.decode_access_token(response.json()['access_token']).username


def test_widget_callback_valid_hash_logs_in(test_client, bot_token):
    params = make_widget_params(telegram_id=111)
    response = test_client.get('/auth/telegram/callback', params=params, follow_redirects=False)
    assert response.status_code == 307, response.text
    assert response.headers['location'] == '/?oauth=ok'
    assert 'refresh_token' in response.cookies
    assert login_username(test_client, response.cookies['refresh_token']) == 'tg_111'


def test_widget_callback_same_telegram_id_reuses_account(test_client, bot_token):
    first = test_client.get(
        '/auth/telegram/callback', params=make_widget_params(telegram_id=222), follow_redirects=False
    )
    second = test_client.get(
        '/auth/telegram/callback', params=make_widget_params(telegram_id=222), follow_redirects=False
    )
    assert login_username(test_client, first.cookies['refresh_token']) == 'tg_222'
    assert login_username(test_client, second.cookies['refresh_token']) == 'tg_222'


def test_widget_callback_invalid_hash_redirects_to_error(test_client, bot_token):
    params = make_widget_params(bot_token='999:OTHER_TOKEN')
    response = test_client.get('/auth/telegram/callback', params=params, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == '/?oauth=error'
    assert 'refresh_token' not in response.cookies


def test_widget_callback_stale_auth_date_redirects_to_error(test_client, bot_token):
    params = make_widget_params(auth_date=int(time.time()) - 3600)
    response = test_client.get('/auth/telegram/callback', params=params, follow_redirects=False)
    assert response.headers['location'] == '/?oauth=error'


def test_widget_callback_disabled_without_bot_token(test_client, monkeypatch):
    monkeypatch.setattr(settings, 'BOT_TOKEN', None)
    response = test_client.get('/auth/telegram/callback', params=make_widget_params(), follow_redirects=False)
    assert response.headers['location'] == '/?oauth=error'
