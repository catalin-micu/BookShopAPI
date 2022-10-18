from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, inputs, fields
from flask_restx.reqparse import RequestParser

import const
from core import authentication

namespace = Namespace('Authentication', 'Used for login and register', '/auth')

parser = RequestParser()
parser.add_argument(
    'email',
    location='json',
    required=True,
    type=inputs.email(check=True)
)
parser.add_argument(
    'passwd',
    location='json',
    required=True,
    type=inputs.regex(const.PASSWORD_REGEX),
    help='Provided password must contain one uppercase letter, one lowercase letter, one digit, one special '
         'character (?=.*?[#?!@$%^&*-]) and must be between 8 and 32 characters')

credentials_dto = namespace.model(
    'CredentialsDTO',
    {
        'email': fields.String(description='User email', required=True),
        'passwd': fields.String(
            description='User password; must contain one uppercase letter, one lowercase letter, one digit, one '
                        'special character (?=.*?[#?!@$%^&*-]) and must be between 8 and 32 characters',
            required=True,
            min_length=8,
            max_length=32
        )
    }
)

login_response = namespace.model(
    'LoginResponse',
    {
        'email': fields.String(description='User email', required=True),
        'access_token': fields.String(description='Successful authentication token'),
        'refresh_token': fields.String(description='Refresh token'),
        'message': fields.String(description='Error message')
    }
)

register_response = namespace.model(
    'RegisterResponse',
    {
        'email': fields.String(description='User email', required=True),
        'is_admin': fields.Boolean(description='Created account permission level', required=True, default=False),
        'error': fields.String(description='Backend error class'),
        'message': fields.String(description='Error message')
    }
)

auth_service = authentication.Authentication()


@namespace.route('/login')
class Login(Resource):
    @namespace.expect(credentials_dto)
    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(404, 'No account associated with provided email')
    @namespace.response(401, 'Wrong password')
    @namespace.marshal_with(login_response)
    def post(self):
        """
        Validates credentials for login
        """
        return auth_service.login(parser.parse_args())


@namespace.route('/register')
class Register(Resource):
    @namespace.expect(credentials_dto)
    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(403, 'Email already in use')
    @namespace.marshal_with(register_response)
    def post(self):
        """
        Validates credentials and creates a new account
        """
        return auth_service.register(parser.parse_args())


@namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @namespace.doc(
        params={'Authorization': {'in': 'headers', 'description': 'Refresh JWT'}}
    )
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(422, 'Only refresh tokens are allowed')
    @namespace.marshal_with(login_response)
    def get(self):
        """
        Refreshes access JWT
        """
        return auth_service.refresh(
            email=get_jwt_identity(),
            refresh_token=request.headers.get('Authorization').replace('Bearer', '').strip()
        )
