from auth.api_errors import ApiErrors
from auth.services import AuthService


def test_login_no_auth_raises_422(test_client):
    response = test_client.post('/auth/login')
    assert response.status_code == 422, response.json()


def test_login_wrong_auth_raises_401(test_client):
    response = test_client.post('/auth/login', data={'username': '_', 'password': '_'})
    assert response.status_code == 401, response.json()
    assert response.json() == ApiErrors.INVALID_LOGIN_OR_PASSWORD.json()


def test_login_with_auth_200(test_client, auth_in_db, password):
    response = test_client.post('/auth/login', data={'username': auth_in_db.username, 'password': password})
    assert response.status_code == 200, response.json()


def test_refresh_token_pair(test_client, refresh_token):
    response = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert response.status_code == 200, response.json()


def test_refresh_no_refresh_token_raises_401(test_client):
    response = test_client.post('/auth/refresh')
    assert response.status_code == 401, response.json()
    assert response.json() == ApiErrors.REFRESH_TOKEN_REQUIRED.json()


def test_refresh_token_is_single_use(test_client, refresh_token):
    first = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert first.status_code == 200, first.json()

    reuse = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert reuse.status_code == 401, reuse.json()

    rotated = first.cookies['refresh_token']
    response = test_client.post('/auth/refresh', cookies={'refresh_token': rotated})
    assert response.status_code == 200, response.json()


def test_refresh_token_without_session_raises_401(test_client, auth_in_db):
    legacy_token = AuthService.create_jwt_token({'id': str(auth_in_db.id), 'token_type': 'refresh'})
    response = test_client.post('/auth/refresh', cookies={'refresh_token': legacy_token})
    assert response.status_code == 401, response.json()


def test_logout_revokes_refresh_token(test_client, refresh_token):
    response = test_client.post('/auth/logout', cookies={'refresh_token': refresh_token})
    assert response.status_code == 204

    response = test_client.post('/auth/refresh', cookies={'refresh_token': refresh_token})
    assert response.status_code == 401, response.json()


def test_logout_without_cookie_is_ok(test_client):
    response = test_client.post('/auth/logout')
    assert response.status_code == 204


def test_login_rate_limited_after_failures(test_client, auth_in_db, password):
    for _ in range(5):
        response = test_client.post('/auth/login', data={'username': auth_in_db.username, 'password': 'wrong'})
        assert response.status_code == 401, response.json()

    response = test_client.post('/auth/login', data={'username': auth_in_db.username, 'password': password})
    assert response.status_code == 429, response.json()
    assert response.json() == ApiErrors.TOO_MANY_LOGIN_ATTEMPTS.json()


def test_login_failures_below_limit_do_not_block(test_client, auth_in_db, password):
    for _ in range(4):
        test_client.post('/auth/login', data={'username': auth_in_db.username, 'password': 'wrong'})

    response = test_client.post('/auth/login', data={'username': auth_in_db.username, 'password': password})
    assert response.status_code == 200, response.json()
