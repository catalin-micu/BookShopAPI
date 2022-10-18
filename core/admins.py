"""
service logic for admins
"""
from functools import wraps
from typing import List, Dict, Tuple, Optional, Literal

from flask_jwt_extended import get_jwt_identity
from orm import users, categories, books


def is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        email = get_jwt_identity()
        users_table = users.Users()
        if not users_table.read(identifier=email)[0][users.UsersColumns.IS_ADMIN]:
            return {'message': 'Logged in user is not admin'}, 403
        return func(*args, **kwargs)

    return wrapper


class Admins:
    """
    Admins business logic; CRUD categories and books
    """
    def __init__(self):
        self.categories = categories.Categories()
        self.books = books.Books()

    def list_categories(self) -> Tuple[List[Dict], int]:
        return self.categories.read(), 200

    def add_category(self, category_name: str) -> Tuple[Dict, int]:
        try:
            return self.categories.create(category_name), 201
        except Exception as e:
            return {'category_name': category_name, 'error': str(e.__class__), 'message': e.args[0]}, 409

    def update_category(self, old_category: str, new_category: str) -> Tuple[Dict, int]:
        try:
            return self.categories.update(old_category, new_category), 200
        except Exception as e:
            return {'category_name': old_category, 'error': str(e.__class__), 'message': 'Old category not found'}, 404

    def delete_category(self, category: str) -> Tuple[Dict, int]:
        try:
            return self.categories.delete(category), 200
        except IndexError as e:
            return {'category_name': category, 'error': str(e.__class__), 'message': 'Category not found'}, 404
        except Exception as e:
            return {'category_name': category, 'error': str(e.__class__), 'message': e.args[0]}, 409

    def list_books(
            self,
            filter_values: Optional[List] = None,
            filter_column: str = categories.CategoriesColumns.CATEGORY_NAME,
            order_column: Optional[Literal[books.BooksColumns.PRICE, books.BooksColumns.YEAR_PUBLISHED]] = None,
            order_descending: Optional[bool] = None
    ) -> Tuple[List[Dict], int]:
        return self.books.read(filter_values, filter_column, order_column, order_descending), 200

    def add_book(self, book: Dict) -> Tuple[Dict, int]:
        try:
            return self.books.create(book), 201
        except Exception as e:
            book.update(error=str(e.__class__), message=e.args[0])
            return book, 409

    def update_book(self, book: Dict) -> Tuple[Dict, int]:
        try:
            return self.books.update({k: v for k, v in book.items() if v}, book[books.BooksColumns.TITLE]), 200
        except IndexError as e:
            book.update(error=str(e.__class__), message='Book not found')
            return book, 404
        except Exception as e:
            book.update(error=str(e.__class__), message=e.args[0])
            return book, 409

    def delete_book(self, title: str) -> Tuple[Dict, int]:
        try:
            return self.books.delete(title), 200
        except IndexError as e:
            return {'title': title, 'error': str(e.__class__), 'message': 'Book not found'}, 404
        except Exception as e:
            return {'title': title, 'error': str(e.__class__), 'message': e.args[0]}, 409
