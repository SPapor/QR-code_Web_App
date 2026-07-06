import pytest


@pytest.fixture
def auth_headers(test_client):
    response = test_client.post('/user/register', json={'username': 'validator', 'password': 'pw12345678'})
    assert response.status_code == 200, response.json()
    return {'Authorization': f"Bearer {response.json()['access_token']}"}


def create(test_client, auth_headers, name='test', link='https://example.com'):
    return test_client.post('/qr_code/', json={'name': name, 'link': link}, headers=auth_headers)


def test_create_valid_link_200(test_client, auth_headers):
    response = create(test_client, auth_headers)
    assert response.status_code == 200, response.json()


def test_create_non_http_link_422(test_client, auth_headers):
    for link in ('ftp://example.com', 'javascript:alert(1)', 'example.com'):
        response = create(test_client, auth_headers, link=link)
        assert response.status_code == 422, link


def test_create_too_long_name_422(test_client, auth_headers):
    response = create(test_client, auth_headers, name='x' * 101)
    assert response.status_code == 422


def test_create_too_long_link_422(test_client, auth_headers):
    response = create(test_client, auth_headers, link='https://example.com/' + 'x' * 2048)
    assert response.status_code == 422


def test_edit_validates_link_too(test_client, auth_headers):
    qr_code = create(test_client, auth_headers).json()
    response = test_client.put(
        f"/qr_code/{qr_code['id']}",
        json={'name': 'test', 'link': 'javascript:alert(1)'},
        headers=auth_headers,
    )
    assert response.status_code == 422
