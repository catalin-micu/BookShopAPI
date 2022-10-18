from flask_restx import Namespace, Resource
from flask_restx.reqparse import RequestParser
from microservice_apis import admins
from core import anonymous

namespace = Namespace('Anonymous users', 'Guest users that are not authenticated', '/anonymous')
anonymous_service = anonymous.AnonymousUsers()


@namespace.route('/')
class AnonymousListing(Resource):
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
        return anonymous_service.list_books(
            filter_values=args['filter-values'],
            filter_column=args['filter'],
            order_column=args['order'],
            order_descending=args['order-descending']
        )
