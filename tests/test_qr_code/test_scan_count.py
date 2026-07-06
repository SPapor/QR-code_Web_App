import pytest


@pytest.fixture
def auth_headers(test_client):
    response = test_client.post('/user/register', json={'username': 'qr_owner', 'password': 'pw12345678'})
    assert response.status_code == 200, response.json()
    return {'Authorization': f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def qr_code(test_client, auth_headers):
    response = test_client.post('/qr_code/', json={'name': 'test', 'link': 'https://example.com'}, headers=auth_headers)
    assert response.status_code == 200, response.json()
    return response.json()


def test_new_code_has_zero_scans(qr_code):
    assert qr_code['scan_count'] == 0
    assert qr_code['last_scan_at'] is None


def test_redirect_increments_scan_count(test_client, auth_headers, qr_code):
    for _ in range(2):
        response = test_client.get(f"/qr_code/{qr_code['id']}", follow_redirects=False)
        assert response.status_code == 302, response.text
        assert response.headers['location'] == 'https://example.com'

    response = test_client.get('/qr_code/', headers=auth_headers)
    assert response.status_code == 200, response.json()
    (item,) = response.json()
    assert item['scan_count'] == 2
    assert item['last_scan_at'] is not None


def test_image_png_default_and_scale(test_client, qr_code):
    small = test_client.get(f"/qr_code/{qr_code['id']}/image")
    big = test_client.get(f"/qr_code/{qr_code['id']}/image?scale=20")
    assert small.headers['content-type'] == 'image/png'
    assert big.headers['content-type'] == 'image/png'
    assert len(big.content) > len(small.content)


def test_image_scale_out_of_range_422(test_client, qr_code):
    response = test_client.get(f"/qr_code/{qr_code['id']}/image?scale=100")
    assert response.status_code == 422


def test_image_svg(test_client, qr_code):
    response = test_client.get(f"/qr_code/{qr_code['id']}/image?fmt=svg")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/svg+xml'
    assert b'<svg' in response.content


def test_stats_empty(test_client, auth_headers, qr_code):
    response = test_client.get(f"/qr_code/{qr_code['id']}/stats?days=7", headers=auth_headers)
    assert response.status_code == 200, response.json()
    stats = response.json()
    assert len(stats['days']) == 7
    assert all(day['count'] == 0 for day in stats['days'])
    assert stats['total'] == 0


def test_stats_counts_today_scans(test_client, auth_headers, qr_code):
    for _ in range(3):
        test_client.get(f"/qr_code/{qr_code['id']}", follow_redirects=False)

    response = test_client.get(f"/qr_code/{qr_code['id']}/stats", headers=auth_headers)
    assert response.status_code == 200, response.json()
    stats = response.json()
    assert len(stats['days']) == 30
    assert stats['days'][-1]['count'] == 3
    assert sum(day['count'] for day in stats['days']) == 3
    assert stats['total'] == 3
    assert stats['last_scan_at'] is not None


def test_stats_requires_auth(test_client, qr_code):
    response = test_client.get(f"/qr_code/{qr_code['id']}/stats")
    assert response.status_code == 401


def test_stats_of_foreign_code_404(test_client, qr_code):
    response = test_client.post('/user/register', json={'username': 'other', 'password': 'pw12345678'})
    other_headers = {'Authorization': f"Bearer {response.json()['access_token']}"}
    response = test_client.get(f"/qr_code/{qr_code['id']}/stats", headers=other_headers)
    assert response.status_code == 404


def test_health(test_client):
    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_redirect_unknown_code_404(test_client):
    response = test_client.get('/qr_code/00000000-0000-0000-0000-000000000000', follow_redirects=False)
    assert response.status_code == 404, response.text
