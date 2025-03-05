from dishka import Provider, Scope, provide

from auth.services import AuthService


class AuthProvider(Provider):
    service = provide(AuthService, scope=Scope.REQUEST)
