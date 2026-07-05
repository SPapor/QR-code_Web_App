import pytest

from auth.rate_limit import RegisterRateLimiter


def register(test_client, username='new_user', password='long_enough_pw'):
    return test_client.post('/user/register', json={'username': username, 'password': password})


def test_register_short_password_422(test_client):
    response = register(test_client, password='short')
    assert response.status_code == 422, response.json()


def test_register_short_username_422(test_client):
    response = register(test_client, username='ab')
    assert response.status_code == 422, response.json()


def test_register_username_with_spaces_422(test_client):
    response = register(test_client, username='has spaces')
    assert response.status_code == 422, response.json()


@pytest.fixture
async def small_register_limit(container):
    limiter = await container.get(RegisterRateLimiter)
    limiter.max_events = 3
    return limiter


async def test_register_rate_limited(test_client, small_register_limit):
    for i in range(3):
        response = register(test_client, username=f'spammer_{i}')
        assert response.status_code == 200, response.json()

    response = register(test_client, username='spammer_3')
    assert response.status_code == 429, response.json()


async def test_register_validation_error_not_counted_by_limiter(test_client, small_register_limit):
    for _ in range(5):
        response = register(test_client, password='short')
        assert response.status_code == 422

    response = register(test_client)
    assert response.status_code == 200, response.json()
