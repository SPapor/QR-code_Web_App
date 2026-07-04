from dishka import Provider, Scope, provide

from telegram_auth.dal import TelegramLinkCodeCrud, TelegramLinkCodeRepo, TelegramLinkCrud, TelegramLinkRepo
from telegram_auth.services import TelegramAuthService


class TelegramAuthProvider(Provider):
    crud = provide(TelegramLinkCrud, scope=Scope.REQUEST)
    repo = provide(TelegramLinkRepo, scope=Scope.REQUEST)
    code_crud = provide(TelegramLinkCodeCrud, scope=Scope.REQUEST)
    code_repo = provide(TelegramLinkCodeRepo, scope=Scope.REQUEST)
    service = provide(TelegramAuthService, scope=Scope.REQUEST)
