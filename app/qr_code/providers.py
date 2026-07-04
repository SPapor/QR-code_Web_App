from dishka import Provider, Scope, provide

from qr_code.dal import QrCodeCrud, QrCodeRepo, ScanEventCrud, ScanEventRepo
from qr_code.services import QrCodeService


class QrCodeProvider(Provider):
    crud = provide(QrCodeCrud, scope=Scope.REQUEST)
    repo = provide(QrCodeRepo, scope=Scope.REQUEST)
    scan_event_crud = provide(ScanEventCrud, scope=Scope.REQUEST)
    scan_event_repo = provide(ScanEventRepo, scope=Scope.REQUEST)
    service = provide(QrCodeService, scope=Scope.REQUEST)
