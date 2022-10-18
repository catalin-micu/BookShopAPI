from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Literal

import const
from orm import books, carts, categories


class RegisteredUsers:
    def __init__(self):
        self.books = books.Books()
        self.carts = carts.Carts()

    def list_books(
            self,
            filter_values: Optional[List] = None,
            filter_column: str = categories.CategoriesColumns.CATEGORY_NAME,
            order_column: Optional[Literal[books.BooksColumns.PRICE, books.BooksColumns.YEAR_PUBLISHED]] = None,
            order_descending: Optional[bool] = None
    ) -> Tuple[List[Dict], int]:
        return [
            i for i in self.books.read(filter_values, filter_column, order_column, order_descending) if i['stock'] > 0
        ], 200

    def add_book_to_cart(self, email: str, book_id: int) -> Tuple[Dict, int]:
        import microservice_apis
        response = {'email': email}
        try:
            book = self._validate_book_stock(book_id)

            new_cart_item = self.carts.create({carts.CartsColumns.EMAIL: email, carts.CartsColumns.BOOK_ID: book_id})
            self.books.update(
                update_data={books.BooksColumns.STOCK: book[books.BooksColumns.STOCK] - 1},
                identifier=book_id,
                identifier_type=books.BooksColumns.BOOK_ID
            )
            response.update(message='Book added to user cart')
            microservice_apis.scheduler.add_job(
                func,
                'date',
                run_date=datetime.now() + timedelta(minutes=const.CART_CLEANUP_TIMEDELTA_MINUTES),
                id=str(new_cart_item[carts.CartsColumns.CART_ID]),
                replace_existing=True,
                args=[new_cart_item[carts.CartsColumns.CART_ID], book_id]
            )
            return response, 201
        except ValueError as e:
            response.update(error=str(e.__class__), message=e.args[0])
            return response, 404
        except Exception as e:
            response.update(error=str(e.__class__), message=e.args[0])
            return response, 403

    def _validate_book_stock(self, book_id: int) -> Dict:
        read_result = self.books.read(filter_column=books.BooksColumns.BOOK_ID, filter_values=[book_id])
        if not read_result:
            raise ValueError(f'No book with ID "{book_id}"')
        book = read_result[0]
        if not book[books.BooksColumns.STOCK]:
            raise Exception(f'Book with ID "{book_id}" is out of stock. It should not be in this request')
        return book

    def delete_book_from_cart(self, email: str, cart_id: int) -> Tuple[Dict, int]:
        import microservice_apis
        """
        Checks if cart item is in the cart of the currently logged user, then removes it
        """
        response = {'email': email}
        try:
            book_id = self._check_if_item_is_in_the_right_cart(cart_id, email)
            self.carts.delete(identifier=cart_id)
            microservice_apis.scheduler.remove_job(str(cart_id))
            self._increase_book_stock(book_id)
            response.update(message='Book deleted from user cart')
            return response, 200
        except ValueError as e:
            response.update(error=str(e.__class__), message=e.args[0])
            return response, 404
        except RuntimeError as e:
            response.update(error=str(e.__class__), message=e.args[0])
            return response, 404

    def _check_if_item_is_in_the_right_cart(self, cart_id: int, email: str) -> int:
        # this method is doing 2 things, not respecting rules of Clean Code... will leave it like this
        user_cart = self.carts.read(email)
        if not user_cart:
            raise ValueError(f'Cart is empty for user "{email}"')
        if cart_id not in [item[carts.CartsColumns.CART_ID] for item in user_cart]:
            raise RuntimeError(f'Item with ID "{cart_id}" not in cart of user "{email}"')
        for item in user_cart:
            if item[carts.CartsColumns.CART_ID] == cart_id:
                return item[carts.CartsColumns.BOOK_ID]

    def _increase_book_stock(self, book_id: int):
        book = self.books.read(filter_column=books.BooksColumns.BOOK_ID, filter_values=[book_id])[0]
        self.books.update(
            update_data={books.BooksColumns.STOCK: book[books.BooksColumns.STOCK] + 1},
            identifier=book_id,
            identifier_type=books.BooksColumns.BOOK_ID
        )

    def get_cart_content(self, email: str) -> Tuple[Dict, int]:
        response = {'email': email}
        cart_content = self.carts.get_cart_content(email)
        if not cart_content:
            response.update(error=str(ValueError.__class__), message=f'Cart is empty for user "{email}"')
            return response, 404
        price, book_titles = sum([item[books.BooksColumns.PRICE] for item in cart_content]), [
            item[books.BooksColumns.TITLE] for item in cart_content
        ]
        response.update(price=price, books=book_titles)
        return response, 200

    def checkout_cart(self, email: str) -> Tuple[Dict, int]:
        result = self.carts.delete(identifier=email, identifier_type=carts.CartsColumns.EMAIL)
        if result:
            self._stop_cart_cleanup_jobs(
                [str(item[carts.CartsColumns.CART_ID]) for item in result]
            )
            return {'email': email, 'message': f'Cart emptied for user "{email}"'}, 200
        else:
            return {'email': email, 'message': f'Cart empty for user "{email}", nothing to checkout'}, 404

    @staticmethod
    def _stop_cart_cleanup_jobs(job_ids: List[str]):
        import microservice_apis
        for job_id in job_ids:
            microservice_apis.scheduler.remove_job(job_id)


global func


def func(cart_id, book_id):
    """
     Cart cleanup function, triggered automatically after 30 minutes from adding a book to cart, that deletes said book
     from your cart and makes it available to the other users (increases book stock by 1)

     According to apscheduler documentation, it needs to be a global function and needs to only have serializable
     parameters (in order to use pickle)
     https://apscheduler.readthedocs.io/en/3.x/userguide.html#adding-jobs
    """
    carts_table = carts.Carts()
    carts_table.delete(cart_id)

    books_table = books.Books()
    book = books_table.read(filter_column=books.BooksColumns.BOOK_ID, filter_values=[book_id])[0]
    books_table.update(
        update_data={books.BooksColumns.STOCK: book[books.BooksColumns.STOCK] + 1},
        identifier=book_id,
        identifier_type=books.BooksColumns.BOOK_ID
    )
    print('AAAAAAAAA')
