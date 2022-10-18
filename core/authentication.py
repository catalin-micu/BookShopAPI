from typing import Dict, Tuple

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from orm import users


class Authentication:
    """
    Authentication business logic; handles register, login and refresh
    """
    def __init__(self):
        self.users = users.Users()

    def register(self, credentials: Dict) -> Tuple[Dict, int]:
        credentials['passwd'] = generate_password_hash(credentials['passwd'], 'sha256')
        try:
            result = self.users.create(credentials)
            return result, 201
        except Exception as e:
            credentials.update({'error': str(e.__class__), 'message': e.args[0]})
            return credentials, 403

    def login(self, credentials: Dict) -> Tuple[Dict, int]:
        email, passwd = credentials['email'], credentials['passwd']
        result = {'email': email}

        db_results = self.users.read(identifier=email)

        if not db_results:
            result.update(message='Email or password are incorrect')
            return result, 404

        passwd_hash = db_results[0]['passwd']
        if not check_password_hash(passwd_hash, passwd):
            result.update(message='Email or password are incorrect')
            return result, 401
        else:
            result.update(
                access_token=create_access_token(identity=email),
                refresh_token=create_refresh_token(identity=email)
            )
            return result, 200

    @staticmethod
    def refresh(email: str, refresh_token: str) -> Tuple[Dict, int]:
        return {
            'email': email,
            'access_token': create_access_token(email),
            'refresh_token': refresh_token
        }, 200
