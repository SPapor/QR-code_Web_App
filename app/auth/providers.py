from dishka import Provider, provide, Scope

from auth.services import AuthService


class AuthProvider(Provider):
    service = provide(AuthService, scope=Scope.REQUEST)
