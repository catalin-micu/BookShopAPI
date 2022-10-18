from dataclasses import dataclass
from typing import Dict, List, Optional, Literal, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Integer, Column, String, select, update, delete, Float, ForeignKey, CheckConstraint

import orm
from orm import books


@dataclass
class CartsColumns:
    CART_ID = 'cart_id'
    EMAIL = 'email'
    BOOK_ID = 'book_id'


CARTS_COLUMNS = [
    CartsColumns.CART_ID,
    CartsColumns.EMAIL,
    CartsColumns.BOOK_ID
]


class Carts(orm.BaseTable):
    __tablename__ = 'carts'

    cart_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'))

    def create(self, cart: Dict) -> Dict:
        """
        Insert a new cart entry
        """
        insert_stmt = insert(Carts).values(cart).returning(Carts.cart_id, Carts.email, Carts.book_id)
        with self.session_factory() as session:
            exec_result = session.execute(insert_stmt).fetchall()
            session.commit()
            return super(Carts, Carts)._transform_returning_row_into_dict(exec_result[0], CARTS_COLUMNS)

    def read(self, email: Optional[str] = None):
        """
        Reads entries in carts. If email is provided, read the cart of the given user
        """
        select_stmt = select(Carts)
        if email:
            select_stmt = select_stmt.where(Carts.email == email)
        with self.session_factory() as session:
            exec_result = session.execute(select_stmt)
            return [super(Carts, Carts)._transform_select_row_into_dict(r, CARTS_COLUMNS) for r in exec_result]

    def delete(
            self, identifier: Union[str, int], identifier_type: str = CartsColumns.CART_ID
    ) -> Union[List[Dict], Dict]:
        """
        Delete one or multiple items from cart. If identifier_type is cart ID, then it deletes only one item.
        If identifier_type is email, it deletes the user's whole cart
        :param identifier: value used to identify the row to delete
        :param identifier_type: column in which to look for `identifier` param
        """
        if identifier_type == CartsColumns.BOOK_ID:
            raise ValueError('Cannot delete all books of same type from all carts')
        delete_stmt = delete(Carts).where(Carts.__table__.c[identifier_type] == identifier).returning(
            Carts.cart_id, Carts.email, Carts.book_id
        )
        with self.session_factory() as session:
            exec_result = session.execute(delete_stmt).fetchall()
            session.commit()
            if len(exec_result) == 1:
                return super(Carts, Carts)._transform_returning_row_into_dict(exec_result[0], CARTS_COLUMNS)
            else:
                return [super(Carts, Carts)._transform_returning_row_into_dict(r, CARTS_COLUMNS) for r in exec_result]

    def get_cart_content(self, email):
        select_stmt = select(books.Books.title, books.Books.price).join(Carts).where(Carts.email == email)
        with self.session_factory() as session:
            exec_result = session.execute(select_stmt)
            return [super(Carts, Carts)._transform_returning_row_into_dict(
                r, [books.BooksColumns.TITLE, books.BooksColumns.PRICE]
            ) for r in exec_result]
