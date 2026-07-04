from dishka import Provider, Scope, provide

from auth.dal import AuthCrud, AuthRepo, RefreshSessionCrud, RefreshSessionRepo
from auth.rate_limit import LoginRateLimiter
from auth.services import AuthService


class AuthProvider(Provider):
    crud = provide(AuthCrud, scope=Scope.REQUEST)
    repo = provide(AuthRepo, scope=Scope.REQUEST)
    refresh_session_crud = provide(RefreshSessionCrud, scope=Scope.REQUEST)
    refresh_session_repo = provide(RefreshSessionRepo, scope=Scope.REQUEST)
    service = provide(AuthService, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def login_rate_limiter(self) -> LoginRateLimiter:
        return LoginRateLimiter()
