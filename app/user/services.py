from auth.services import AuthService
from user.dal import UserRepo


class UserService:
    def __init__(self, user_repo: UserRepo, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service
