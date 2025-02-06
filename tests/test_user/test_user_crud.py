from typing import Mapping
from uuid import UUID

import pytest


async def test_user_crud_create(user_crud):
    id_ = await user_crud.create({"username": "TestName"})
    assert isinstance(id_, UUID)


async def test_user_crud_get_by_id(user_crud, user_in_db):
    user = await user_crud.get_by_id(user_in_db['id'])
    assert isinstance(user, Mapping)
    assert user['id'] == user_in_db['id']
    assert user['username'] == user_in_db['username']


async def test_user_crud_get_many_by_ids(user_crud, users_in_db):
    ids = [user['id'] for user in users_in_db]
    users = await user_crud.get_many_by_ids(ids)
    assert len(users) == len(users_in_db)
    for user, db_user in zip(users, users_in_db):
        assert isinstance(user, Mapping)
        assert user['username'] == db_user['username']


@pytest.mark.parametrize('users_number', [2])
async def test_user_crud_create_many(user_crud, users_payload):
    ids = await user_crud.create_many(users_payload)
    assert len(ids) == len(users_payload)


@pytest.mark.parametrize('users_number', [2])
async def test_user_crud_create_and_get_many(user_crud, users_payload):
    users = await user_crud.create_and_get_many(users_payload)
    assert len(users) == len(users_payload)
    for user, payload in zip(users, users_payload):
        assert isinstance(user, Mapping)
        assert user['username'] == payload['username']


async def test_user_crud_update(user_crud, user_in_db):
    await user_crud.update({"id": user_in_db['id'], "username": f'{user_in_db["username"]}_updated'})
    user = await user_crud.get_by_id(user_in_db['id'])
    assert user['username'] == f'{user_in_db["username"]}_updated'


async def test_user_crud_update_many(user_crud, users_in_db):
    payload = [dict(user) | {"username": f'{user["username"]}_updated'} for user in users_in_db]
    await user_crud.update_many(payload)
    users = await user_crud.get_many_by_ids([user['id'] for user in users_in_db])
    for user, payload in zip(users, payload):
        assert user['username'] == payload['username']


async def test_user_crud_delete(user_crud, user_in_db):
    await user_crud.delete(user_in_db['id'])
    user = await user_crud.get_by_id(user_in_db['id'])
    assert user is None


async def test_user_crud_delete_many(user_crud, users_in_db):
    await user_crud.delete_many([user['id'] for user in users_in_db])
    users = await user_crud.get_many_by_ids([user['id'] for user in users_in_db])
    assert not users


@pytest.mark.parametrize('users_number', [0, 1, 2, 5, 10])
async def test_user_crud_count(user_crud, users_in_db, users_number):
    assert await user_crud.count() == users_number


@pytest.mark.parametrize('users_number', [0, 1, 2, 5, 10])
async def test_user_crud_get_all(user_crud, users_in_db, users_number):
    assert len(await user_crud.get_all()) == users_number
    for user, db_user in zip(await user_crud.get_all(), users_in_db):
        assert user['username'] == db_user['username']
