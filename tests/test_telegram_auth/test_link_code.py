import time

import pytest

from auth.services import AuthService
from core.settings import settings
from telegram_auth import services as telegram_services


@pytest.fixture
def bot_secret(monkeypatch):
    monkeypatch.setattr(settings, 'BOT_SHARED_SECRET', 'test-bot-secret')
    return settings.BOT_SHARED_SECRET


@pytest.fixture
def site_account(test_client):
    response = test_client.post('/user/register', json={'username': 'site_user', 'password': 'pw'})
    assert response.status_code == 200, response.json()
    return response.json()['access_token']


def issue_code(test_client, access_token: str) -> str:
    response = test_client.post('/auth/telegram/link_code', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200, response.json()
    return response.json()['code']


def test_link_code_requires_auth(test_client):
    response = test_client.post('/auth/telegram/link_code')
    assert response.status_code == 401, response.json()


def test_link_by_code_links_telegram_to_account(test_client, bot_secret, site_account):
    code = issue_code(test_client, site_account)
    response = test_client.post(
        '/auth/telegram/link_by_code',
        json={'telegram_id': 777, 'code': code},
        headers={'X-Bot-Secret': bot_secret},
    )
    assert response.status_code == 200, response.json()
    assert AuthService.decode_access_token(response.json()['access_token']).username == 'site_user'

    # subsequent exchange for the same telegram_id lands in the linked account
    response = test_client.post(
        '/auth/telegram/exchange', json={'telegram_id': 777}, headers={'X-Bot-Secret': bot_secret}
    )
    assert AuthService.decode_access_token(response.json()['access_token']).username == 'site_user'


def test_link_by_code_is_single_use(test_client, bot_secret, site_account):
    code = issue_code(test_client, site_account)
    headers = {'X-Bot-Secret': bot_secret}
    first = test_client.post('/auth/telegram/link_by_code', json={'telegram_id': 778, 'code': code}, headers=headers)
    assert first.status_code == 200
    second = test_client.post('/auth/telegram/link_by_code', json={'telegram_id': 779, 'code': code}, headers=headers)
    assert second.status_code == 400, second.json()


def test_link_by_code_expired(test_client, bot_secret, site_account, monkeypatch):
    code = issue_code(test_client, site_account)
    real_time = time.time()
    monkeypatch.setattr(telegram_services.time, 'time', lambda: real_time + telegram_services.LINK_CODE_TTL_SECONDS + 1)
    response = test_client.post(
        '/auth/telegram/link_by_code',
        json={'telegram_id': 780, 'code': code},
        headers={'X-Bot-Secret': bot_secret},
    )
    assert response.status_code == 400, response.json()


def test_link_by_code_unknown_code(test_client, bot_secret):
    response = test_client.post(
        '/auth/telegram/link_by_code',
        json={'telegram_id': 781, 'code': 'nope'},
        headers={'X-Bot-Secret': bot_secret},
    )
    assert response.status_code == 400, response.json()


def test_link_by_code_moves_qr_codes_from_auto_account(test_client, bot_secret, site_account):
    # bot user starts as an auto account and creates a QR code
    response = test_client.post(
        '/auth/telegram/exchange', json={'telegram_id': 900}, headers={'X-Bot-Secret': bot_secret}
    )
    bot_access = response.json()['access_token']
    response = test_client.post(
        '/qr_code/',
        params={'name': 'from bot', 'link': 'https://example.com'},
        headers={'Authorization': f'Bearer {bot_access}'},
    )
    assert response.status_code == 200, response.json()

    # linking moves the QR code to the site account
    code = issue_code(test_client, site_account)
    response = test_client.post(
        '/auth/telegram/link_by_code',
        json={'telegram_id': 900, 'code': code},
        headers={'X-Bot-Secret': bot_secret},
    )
    assert response.status_code == 200, response.json()
    response = test_client.get('/qr_code/', headers={'Authorization': f'Bearer {site_account}'})
    assert [qr['name'] for qr in response.json()] == ['from bot']
