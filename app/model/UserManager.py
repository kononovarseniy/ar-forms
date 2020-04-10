from data import UserRepository


class UserManager:
    @staticmethod
    def register(login, display_name, password):
        return UserRepository.add_user(login, display_name, password)

    @staticmethod
    def login(login, password):
        return UserRepository.get_user_by_credentials(login, password)
