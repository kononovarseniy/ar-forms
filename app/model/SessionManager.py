from flask import session

from data import UserRepository


class SessionManager:
    @staticmethod
    def get_user():
        if 'user_id' in session:
            user_id = session['user_id']
            return UserRepository.get_user_by_id(user_id)

    @staticmethod
    def start_session(user):
        session['user_id'] = user.id

    @staticmethod
    def stop_session():
        session.pop('user_id', None)
