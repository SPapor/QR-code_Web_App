from dishka import Provider, Scope, provide

from qr_code.dal import QrCodeCrud, QrCodeRepo


class QrCodeProvider(Provider):
    crud = provide(QrCodeCrud, scope=Scope.REQUEST)
    repo = provide(QrCodeRepo, scope=Scope.REQUEST)
