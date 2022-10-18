from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

from microservice_apis import admins
from core import registered_users

namespace = Namespace('Registered users', 'Registered user actions', '/user-actions')

book_dto = namespace.model(
    'BookDTO',
    {'title': fields.String(description='Title of the book', required=True)}
)

cart_management_response = namespace.model(
    'CartManagementResponse',
    {
        'email': fields.String(description='Cart owner', required=True),
        'error': fields.String(description='Backend error class'),
        'message': fields.String(description='Description message', required=True)
    }
)

cart_content_response = namespace.model(
    'CartContentResponse',
    {
        'email': fields.String(description='User email', required=True),
        'price': fields.Float(description='Total price of all the books'),
        'books': fields.List(fields.String(description='Book titles')),
        'error': fields.String(description='Backend error class'),
        'message': fields.String(description='Error message')
    }
)


registered_users_service = registered_users.RegisteredUsers()


@namespace.route('/')
class RegisteredUserActions(Resource):
    @namespace.doc(
        params={
            'filter': {'in': 'query', 'description': 'Field to filter by'},
            'filter-values': {'in': 'query', 'description': 'Accepted field values'},
            'order': {'in': 'query', 'description': 'Field to order by'},
            'order-descending': {'in': 'query', 'description': 'Whether to order descending or ascending'},
        }
    )
    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.marshal_list_with(admins.books_response)
    @jwt_required()
    def get(self):
        """
        List available books, based on filtering criteria if provided. Books with stock = 0 are excluded.
        Filtering can be done on any column, but only with exact values: you cannot specify a range for price for
        example... It is also possible to filter by category name.
        You can also order results by price or by year, either ascending or descending.
        """
        parser = RequestParser()
        parser.add_argument(
            'filter',
            location='args',
            choices=('title', 'year_published', 'author', 'price', 'category_name', 'stock')
        )
        parser.add_argument('filter-values', location='args', action='split')
        parser.add_argument('order', location='args', choices=('price', 'year'))
        parser.add_argument('order-descending', location='args', type=bool, default=False)

        args = parser.parse_args()
        return registered_users_service.list_books(
            filter_values=args['filter-values'],
            filter_column=args['filter'],
            order_column=args['order'],
            order_descending=args['order-descending']
        )

    @jwt_required()
    @namespace.doc(params={'book_id': {'in': 'json', 'description': 'Book to add in cart'}})
    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(422, 'Signature verification failed')
    @namespace.response(403, 'Book is out of stock. It should not be in this request')
    @namespace.response(404, 'No book with given ID')
    @namespace.marshal_with(cart_management_response)
    def post(self):
        """
        Add book in cart

        steps:
         - check book validity (existence and stock)
         - add entry to cart
         - decrease quantity in books

         *Note*: After 30 minutes, the book will automatically be taken out of the cart and made available to the other
         users (book stock will be increased by 1)
        """
        parser = RequestParser()
        parser.add_argument('book_id', location='json', required=True, type=int)
        return registered_users_service.add_book_to_cart(get_jwt_identity(), parser.parse_args()['book_id'])

    @jwt_required()
    @namespace.doc(params={'cart_id': {'in': 'json', 'description': 'Cart item to remove'}})
    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(422, 'Signature verification failed')
    @namespace.response(404, 'Resource not found')
    @namespace.marshal_with(cart_management_response)
    def delete(self):
        """
        Delete book from cart

        steps:
         - check if book in current user cart
         - remove from cart
         - increase quantity in books
        """
        parser = RequestParser()
        parser.add_argument('cart_id', location='json', required=True, type=int)
        return registered_users_service.delete_book_from_cart(get_jwt_identity(), parser.parse_args()['cart_id'])


@namespace.route('/cart')
class Cart(Resource):
    @jwt_required()
    @namespace.response(422, 'Signature verification failed')
    @namespace.response(404, 'Cart is empty')
    @namespace.marshal_with(cart_content_response)
    def get(self):
        """
        Get all items in current cart
        """
        return registered_users_service.get_cart_content(get_jwt_identity())

    @jwt_required()
    @namespace.response(422, 'Signature verification failed')
    @namespace.response(404, 'Cart is empty')
    def delete(self):
        """
        Buy items available in cart
        """
        return registered_users_service.checkout_cart(get_jwt_identity())
