from dishka import Provider, Scope, provide

from user.dao import UserCrud, UserRepo, UserSerializer


class UserProvider(Provider):
    serializer = provide(UserSerializer, scope=Scope.APP)
    crud = provide(UserCrud, scope=Scope.REQUEST)
    repo = provide(UserRepo, scope=Scope.REQUEST)
