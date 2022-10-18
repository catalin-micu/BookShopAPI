from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser
from core import admins
from orm import books

namespace = Namespace('Admins', 'Server administrators that can alter database content', '/admins')


categories_response = namespace.model(
    'CategoriesResponse',
    {
        'category_id': fields.String(description='Internal category ID'),
        'category_name': fields.String(description='Name of the category'),
        'error': fields.String(description='Backend error class'),
        'message': fields.String(description='Error message')
    }
)

categories_dto = namespace.model(
    'CategoriesDTO',
    {'category_name': fields.String(description='Name of the category')}
)


admins_service = admins.Admins()


@namespace.route('/categories')
class CategoriesManagement(Resource):
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.marshal_list_with(categories_response)
    @jwt_required()
    @admins.is_admin
    def get(self):
        """
        List available categories
        """
        return admins_service.list_categories()

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(409, 'Database constraints violation')
    @namespace.expect(categories_dto)
    @namespace.marshal_with(categories_response)
    @jwt_required()
    @admins.is_admin
    def post(self):
        """
        Create a category
        """
        parser = RequestParser()
        parser.add_argument('category_name', location='json', required=True)
        return admins_service.add_category(parser.parse_args()['category_name'])

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(404, 'Category not found')
    @namespace.expect(categories_dto)
    @namespace.marshal_with(categories_response)
    @jwt_required()
    @admins.is_admin
    def patch(self):
        """
        Update a category
        """
        parser = RequestParser()
        parser.add_argument('old_category', location='json', required=True)
        parser.add_argument('new_category', location='json', required=True)
        return admins_service.update_category(**parser.parse_args())

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(404, 'Category not found')
    @namespace.response(409, 'Database constraints violation')
    @namespace.expect(categories_dto)
    @namespace.marshal_with(categories_response)
    @jwt_required()
    @admins.is_admin
    def delete(self):
        """
        Delete a category; only possible of books aren't assigned to it
        """
        parser = RequestParser()
        parser.add_argument('category_name', location='json', required=True)
        return admins_service.delete_category(parser.parse_args()['category_name'])


books_response = namespace.model(
    'BooksResponse',
    {
        'book_id': fields.Integer(description='Internal ID'),
        'title': fields.String(description='Title of the book', required=True),
        'year_published': fields.Integer(description='Year the book came out', required=True),
        'author': fields.String(description='Book author', required=True),
        'price': fields.Integer(description='Book price in USD', required=True),
        'category_id': fields.Integer(description='ID of the category it belongs to', required=True),
        'stock': fields.Integer(description='Copies left in stock', required=True),
        'error': fields.String(description='Backend error class'),
        'message': fields.String(description='Error message')
    }
)


books_dto = namespace.model(
    'BooksDTO',
    {
        'title': fields.String(description='Title of the book', required=True),
        'year_published': fields.Integer(description='Year the book came out'),
        'author': fields.String(description='Book author'),
        'price': fields.Integer(description='Book price in USD'),
        'category_id': fields.Integer(description='ID of the category it belongs to'),
        'stock': fields.Integer(description='Copies left in stock')
    }
)


@namespace.route('/books')
class BooksManagement(Resource):
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
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.marshal_list_with(books_response)
    @jwt_required()
    @admins.is_admin
    def get(self):
        """
        Reads books based on generic filtering capability. Filtering can be done on any column, but only with exact
        values: you cannot specify a range for price for example... It is also possible to filter by category name, even
        though current table has category_id as column -> join with Categories table is used. You can also order results
        by price or by year, either ascending or descending.
        """
        parser = RequestParser()
        parser.add_argument(
            'filter',
            location='args',
            choices=(
                *books.BOOKS_COLUMNS, 'category_name'
            )
        )
        parser.add_argument('filter-values', location='args', action='split')
        parser.add_argument('order', location='args', choices=('price', 'year'))
        parser.add_argument('order-descending', location='args', type=bool, default=False)

        args = parser.parse_args()
        return admins_service.list_books(
            filter_values=args['filter-values'],
            filter_column=args['filter'],
            order_column=args['order'],
            order_descending=args['order-descending']
        )

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(409, 'Database constraints violation')
    @namespace.expect(books_dto)
    @namespace.marshal_with(books_response)
    @jwt_required()
    @admins.is_admin
    def post(self):
        """
        Add a new book. Book title must be unique, price and stock must be positive, year must be in
        interval (1000, curr_year], it must belong to a category
        """
        parser = RequestParser()
        parser.add_argument('title', location='json', required=True)
        parser.add_argument('year_published', location='json', required=True, type=int)
        parser.add_argument('author', location='json', required=True)
        parser.add_argument('price', location='json', required=True, type=int)
        parser.add_argument('category_id', location='json', required=True, type=int)
        parser.add_argument('stock', location='json', required=True, type=int)

        return admins_service.add_book(parser.parse_args())

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(404, 'Book not found')
    @namespace.response(409, 'Database constraints violation')
    @namespace.expect(books_dto)
    @namespace.marshal_with(books_response)
    @jwt_required()
    @admins.is_admin
    def patch(self):
        """
        Update book based on title. Everything can be changed except for the ID
        """
        parser = RequestParser()
        parser.add_argument('title', location='json', required=True)
        parser.add_argument('year_published', location='json', type=int)
        parser.add_argument('author', location='json')
        parser.add_argument('price', location='json', type=int)
        parser.add_argument('category_id', location='json', type=int)

        return admins_service.update_book(parser.parse_args())

    @namespace.response(400, 'Input payload validation failed')
    @namespace.response(401, 'Missing Authorization Header')
    @namespace.response(403, 'Logged in user is not admin')
    @namespace.response(404, 'Book not found')
    @namespace.response(409, 'Database constraints violation')
    @namespace.expect(books_dto)
    @namespace.marshal_with(books_response)
    @jwt_required()
    @admins.is_admin
    def delete(self):
        """
        Delete a book. You cannot delete it if it's in somebody's cart
        """
        parser = RequestParser()
        parser.add_argument('title', location='json', required=True)
        return admins_service.delete_book(parser.parse_args()['title'])
