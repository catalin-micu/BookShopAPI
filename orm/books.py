from dataclasses import dataclass
from typing import Dict, List, Optional, Literal, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Integer, Column, String, select, update, delete, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

import orm

from orm import categories, carts  # leave this import here!! without it books table cannot create relationship


@dataclass
class BooksColumns:
    BOOK_ID = 'book_id'
    TITLE = 'title'
    YEAR_PUBLISHED = 'year_published'
    AUTHOR = 'author'
    PRICE = 'price'
    CATEGORY_ID = 'category_id'
    STOCK = 'stock'


BOOKS_COLUMNS = [
    BooksColumns.BOOK_ID,
    BooksColumns.TITLE,
    BooksColumns.YEAR_PUBLISHED,
    BooksColumns.AUTHOR,
    BooksColumns.PRICE,
    BooksColumns.CATEGORY_ID,
    BooksColumns.STOCK
]


RETURNING_BOOKS_COLUMNS = [
    BooksColumns.TITLE,
    BooksColumns.YEAR_PUBLISHED,
    BooksColumns.AUTHOR,
    BooksColumns.PRICE,
    BooksColumns.CATEGORY_ID,
    BooksColumns.STOCK
]


BOOKS_UNIQUE_IDENTIFIERS = [BooksColumns.BOOK_ID, BooksColumns.TITLE]


class Books(orm.BaseTable):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    year_published = Column(
        Integer,
        CheckConstraint(r'year_published > 1000'),
        CheckConstraint(r"year_published <= date_part('year', current_date)"),
        nullable=False
    )
    author = Column(String, nullable=False)
    price = Column(Float, CheckConstraint(r'price > 0'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    stock = Column(Integer, CheckConstraint(r'stock >= 0'), nullable=False)

    carts = relationship('Carts')

    def create(self, book: Dict) -> Dict:
        """
        Insert a new book
        """
        insert_stmt = insert(Books).values(book).returning(
            Books.book_id, Books.title, Books.year_published, Books.author, Books.price, Books.category_id, Books.stock
        )
        with self.session_factory() as session:
            exec_result = session.execute(insert_stmt).fetchall()
            session.commit()
            return super(Books, Books)._transform_returning_row_into_dict(exec_result[0], RETURNING_BOOKS_COLUMNS)

    def read(
            self,
            filter_values: Optional[List] = None,
            filter_column: str = categories.CategoriesColumns.CATEGORY_NAME,
            order_column: Optional[Literal[BooksColumns.PRICE, BooksColumns.YEAR_PUBLISHED]] = None,
            order_descending: Optional[bool] = None
    ) -> List[Dict]:
        """
        Reads books based on generic filtering capability. Filtering can be done on any column, but only with exact
        values: you cannot specify a range for price for example... It is also possible to filter by category name, even
        though current table has category_id as column -> join with Categories table is used. You can also order results
        by price or by year, either ascending or descending.

        **FUTURE DEVELOPMENT**: Handle intervals for price and year
        :param filter_values: exact values of book columns, used for the IN clause
        :param filter_column: column used for filtering
        :param order_column: column used for ordering
        :param order_descending: whether to sort in descending order, or ascending
        :return: filtered and sorted books
        """
        select_stmt = select(Books)
        if filter_values and filter_column:
            if filter_column == categories.CategoriesColumns.CATEGORY_NAME:
                select_stmt = select_stmt.join(categories.Categories).where(
                    categories.Categories.category_name.in_(filter_values)
                )
            else:
                select_stmt = select_stmt.where(
                    Books.__table__.c[filter_column].in_(filter_values)
                )
        if order_column:
            select_stmt = select_stmt.order_by(
                Books.__table__.c[order_column].desc() if order_descending else Books.__table__.c[order_column]
            )
        with self.session_factory() as session:
            exec_result = session.execute(select_stmt)
            return [super(Books, Books)._transform_select_row_into_dict(r, BOOKS_COLUMNS) for r in exec_result]

    def update(self, update_data: Dict, identifier: Union[str, int], identifier_type: str = BooksColumns.TITLE) -> Dict:
        """
        Updates one book
        :param update_data: new data of book
        :param identifier: value used to identify the row to update
        :param identifier_type: column in which to look for `identifier` param
        """
        if identifier_type not in BOOKS_UNIQUE_IDENTIFIERS:
            raise ValueError(f'Cannot identify book based on column "{identifier_type}"')

        update_stmt = update(Books).where(Books.__table__.c[identifier_type] == identifier).values(
            update_data
        ).returning(
            Books.book_id, Books.title, Books.year_published, Books.author, Books.price, Books.category_id, Books.stock
        )
        with self.session_factory() as session:
            exec_result = session.execute(update_stmt).fetchall()
            session.commit()
            return super(Books, Books)._transform_returning_row_into_dict(exec_result[0], BOOKS_COLUMNS)

    def delete(self, identifier: str, identifier_type: str = BooksColumns.TITLE) -> Dict:
        """
        Deletes a book
        :param identifier: value used to identify the row to delete
        :param identifier_type: column in which to look for `identifier` param
        """
        if identifier_type not in BOOKS_UNIQUE_IDENTIFIERS:
            raise ValueError(f'Cannot identify book based on column "{identifier_type}"')
        delete_stmt = delete(Books).where(Books.__table__.c[identifier_type] == identifier).returning(
            Books.title, Books.year_published, Books.author, Books.price, Books.category_id, Books.stock
        )
        with self.session_factory() as session:
            exec_result = session.execute(delete_stmt).fetchall()
            session.commit()
            return super(Books, Books)._transform_returning_row_into_dict(exec_result[0], RETURNING_BOOKS_COLUMNS)
