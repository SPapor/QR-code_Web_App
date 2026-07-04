from auth.errors import AuthError


class GoogleAuthError(AuthError):
    pass


class GoogleIntegrationDisabledError(GoogleAuthError):
    pass


class InvalidGoogleStateError(GoogleAuthError):
    pass


class GoogleExchangeFailedError(GoogleAuthError):
    pass
