from dishka import Provider, Scope, provide

from user.dao import UserCrud, UserSerializer


class UserProvider(Provider):
    serializer = provide(UserSerializer, scope=Scope.APP)
    crud = provide(UserCrud, scope=Scope.REQUEST)
