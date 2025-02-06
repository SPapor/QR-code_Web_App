def test_user_serializer_serialize(user_serializer, user):
    user_dto = user_serializer.serialize(user)
    assert user_dto['id'] == user.id
    assert user_dto['username'] == user.username


def test_user_serializer_deserialize(user_serializer, user_dto):
    user = user_serializer.deserialize(user_dto)
    assert user.id == user_dto['id']
    assert user.username == user_dto['username']
