from auth.errors import AuthError


class TelegramAuthError(AuthError):
    pass


class InvalidBotSecretError(TelegramAuthError):
    pass


class BotIntegrationDisabledError(TelegramAuthError):
    pass


class TargetAccountAlreadyLinkedError(TelegramAuthError):
    pass


class InvalidTelegramWidgetDataError(TelegramAuthError):
    pass


class InvalidLinkCodeError(TelegramAuthError):
    pass
