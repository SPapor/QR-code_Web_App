import pytest


@pytest.fixture
def auth_headers(test_client):
    response = test_client.post('/user/register', json={'username': 'stylist', 'password': 'pw12345678'})
    assert response.status_code == 200, response.json()
    return {'Authorization': f"Bearer {response.json()['access_token']}"}


def create(test_client, auth_headers, **extra):
    payload = {'name': 'styled', 'link': 'https://example.com', **extra}
    return test_client.post('/qr_code/', json=payload, headers=auth_headers)


def test_create_default_style(test_client, auth_headers):
    response = create(test_client, auth_headers)
    assert response.status_code == 200, response.json()
    body = response.json()
    assert body['fill_color'] == '#000000'
    assert body['fill_color2'] is None
    assert body['back_color'] == '#ffffff'
    assert body['style'] == 'square'


def test_create_custom_style_roundtrip(test_client, auth_headers):
    response = create(
        test_client,
        auth_headers,
        fill_color='#2A5E8C',
        fill_color2='#7C2D12',
        back_color='#F5EFE6',
        style='rounded',
    )
    assert response.status_code == 200, response.json()
    body = response.json()
    assert body['fill_color'] == '#2A5E8C'
    assert body['fill_color2'] == '#7C2D12'
    assert body['back_color'] == '#F5EFE6'
    assert body['style'] == 'rounded'


def test_update_style(test_client, auth_headers):
    qr_code = create(test_client, auth_headers).json()
    response = test_client.put(
        f"/qr_code/{qr_code['id']}",
        json={'name': 'styled', 'link': 'https://example.com', 'fill_color': '#7C3E80', 'style': 'dots'},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json()['fill_color'] == '#7C3E80'
    assert response.json()['style'] == 'dots'


def test_bad_hex_422(test_client, auth_headers):
    for bad in ('red', '#fff', '#12345', '123456', '#12345g'):
        response = create(test_client, auth_headers, fill_color=bad)
        assert response.status_code == 422, bad


def test_unknown_style_422(test_client, auth_headers):
    response = create(test_client, auth_headers, style='hexagon')
    assert response.status_code == 422


def test_low_contrast_422(test_client, auth_headers):
    response = create(test_client, auth_headers, fill_color='#ffff00')  # yellow on white
    assert response.status_code == 422


def test_low_contrast_gradient_422(test_client, auth_headers):
    response = create(test_client, auth_headers, fill_color='#000000', fill_color2='#eeeeee')
    assert response.status_code == 422


def test_styled_image_differs_from_default(test_client, auth_headers):
    plain = create(test_client, auth_headers).json()
    styled = create(test_client, auth_headers, fill_color='#2A5E8C', style='dots').json()
    plain_png = test_client.get(f"/qr_code/{plain['id']}/image").content
    styled_png = test_client.get(f"/qr_code/{styled['id']}/image").content
    assert plain_png != styled_png


def test_svg_uses_fill_and_back_colors(test_client, auth_headers):
    qr_code = create(test_client, auth_headers, fill_color='#2A5E8C', back_color='#F5EFE6').json()
    response = test_client.get(f"/qr_code/{qr_code['id']}/image?fmt=svg")
    assert response.status_code == 200
    assert b'#2A5E8C' in response.content
    assert b'#F5EFE6' in response.content


def test_style_preview_requires_auth(test_client):
    response = test_client.get('/qr_code/style/preview')
    assert response.status_code == 401


def test_style_preview_renders_png(test_client, auth_headers):
    response = test_client.get(
        '/qr_code/style/preview',
        params={'fill_color': '#2A5E8C', 'fill_color2': '#7C2D12', 'back_color': '#ffffff', 'style': 'rounded'},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.headers['content-type'] == 'image/png'


def test_style_preview_validates_contrast(test_client, auth_headers):
    response = test_client.get(
        '/qr_code/style/preview',
        params={'fill_color': '#ffff00'},
        headers=auth_headers,
    )
    assert response.status_code == 422
