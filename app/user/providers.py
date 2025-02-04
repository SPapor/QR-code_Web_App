from dishka import Provider, Scope, provide

from user.dao import UserCrud


class UserProvider(Provider):
    crud = provide(UserCrud, scope=Scope.REQUEST)
