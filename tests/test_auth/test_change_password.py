OLD_PW = 'old_password_1'
NEW_PW = 'new_password_2'


def register(test_client, password=OLD_PW):
    response = test_client.post('/user/register', json={'username': 'pw_user', 'password': password})
    assert response.status_code == 200, response.json()
    return response


def change(test_client, token, old, new):
    return test_client.post(
        '/auth/change_password',
        json={'old_password': old, 'new_password': new},
        headers={'Authorization': f'Bearer {token}'},
    )


def test_change_password_requires_auth(test_client):
    response = test_client.post('/auth/change_password', json={'old_password': 'x', 'new_password': 'y' * 8})
    assert response.status_code == 401


def test_change_password_wrong_current_400(test_client):
    token = register(test_client).json()['access_token']
    response = change(test_client, token, 'not-the-password', NEW_PW)
    assert response.status_code == 400, response.json()
    assert response.json()['error_code'] == 'auth.0007'


def test_change_password_too_short_new_422(test_client):
    token = register(test_client).json()['access_token']
    response = change(test_client, token, OLD_PW, 'short')
    assert response.status_code == 422


def test_change_password_success_and_old_sessions_revoked(test_client):
    first = register(test_client)
    token = first.json()['access_token']
    old_refresh_cookie = first.cookies['refresh_token']

    response = change(test_client, token, OLD_PW, NEW_PW)
    assert response.status_code == 200, response.json()
    assert 'access_token' in response.json()

    # old password no longer works, new one does
    assert test_client.post('/auth/login', data={'username': 'pw_user', 'password': OLD_PW}).status_code == 401
    assert test_client.post('/auth/login', data={'username': 'pw_user', 'password': NEW_PW}).status_code == 200

    # the pre-change refresh session was revoked
    test_client.cookies.set('refresh_token', old_refresh_cookie)
    assert test_client.post('/auth/refresh').status_code == 401


def test_me_reports_username_and_links(test_client):
    token = register(test_client).json()['access_token']
    response = test_client.get('/user/me', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200, response.json()
    assert response.json() == {'username': 'pw_user', 'telegram_linked': False, 'google_linked': False}


def test_me_requires_auth(test_client):
    assert test_client.get('/user/me').status_code == 401
