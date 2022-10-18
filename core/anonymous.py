from typing import List, Dict, Tuple, Optional, Literal

from orm import books, categories


class AnonymousUsers:
    def __init__(self):
        self.books = books.Books()

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
