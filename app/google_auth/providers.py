from dishka import Provider, Scope, provide

from google_auth.dal import GoogleLinkCrud, GoogleLinkRepo
from google_auth.services import GoogleAuthService


class GoogleAuthProvider(Provider):
    crud = provide(GoogleLinkCrud, scope=Scope.REQUEST)
    repo = provide(GoogleLinkRepo, scope=Scope.REQUEST)
    service = provide(GoogleAuthService, scope=Scope.REQUEST)
