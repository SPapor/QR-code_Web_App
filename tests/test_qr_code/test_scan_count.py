import pytest


@pytest.fixture
def auth_headers(test_client):
    response = test_client.post('/user/register', json={'username': 'qr_owner', 'password': 'pw'})
    assert response.status_code == 200, response.json()
    return {'Authorization': f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def qr_code(test_client, auth_headers):
    response = test_client.post('/qr_code/?name=test&link=https://example.com', headers=auth_headers)
    assert response.status_code == 200, response.json()
    return response.json()


def test_new_code_has_zero_scans(qr_code):
    assert qr_code['scan_count'] == 0


def test_redirect_increments_scan_count(test_client, auth_headers, qr_code):
    for _ in range(2):
        response = test_client.get(f"/qr_code/{qr_code['id']}", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers['location'] == 'https://example.com'

    response = test_client.get('/qr_code/', headers=auth_headers)
    assert response.status_code == 200, response.json()
    (item,) = response.json()
    assert item['scan_count'] == 2


def test_redirect_unknown_code_404(test_client):
    response = test_client.get('/qr_code/00000000-0000-0000-0000-000000000000', follow_redirects=False)
    assert response.status_code == 404, response.text
