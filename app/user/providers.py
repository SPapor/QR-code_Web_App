from dishka import Provider, Scope, provide

from auth.rate_limit import RegisterRateLimiter
from user.dal import UserCrud, UserRepo
from user.services import UserService


class UserProvider(Provider):
    crud = provide(UserCrud, scope=Scope.REQUEST)
    repo = provide(UserRepo, scope=Scope.REQUEST)
    service = provide(UserService, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def register_rate_limiter(self) -> RegisterRateLimiter:
        return RegisterRateLimiter()
