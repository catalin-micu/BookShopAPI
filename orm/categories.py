from dataclasses import dataclass
from typing import Dict, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Integer, Column, String, select, update, delete
from sqlalchemy.orm import relationship

import orm


@dataclass
class CategoriesColumns:
    CATEGORY_ID = 'category_id'
    CATEGORY_NAME = 'category_name'


CATEGORIES_COLUMNS = [CategoriesColumns.CATEGORY_ID, CategoriesColumns.CATEGORY_NAME]


RETURNING_CATEGORIES_COLUMNS = [CategoriesColumns.CATEGORY_NAME]


class Categories(orm.BaseTable):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False, unique=True)     # should've placed constraints of length here

    books = relationship('Books')

    def create(self, category_name: str) -> Dict:
        """
        inserts a new category in the db if entry doesn't already exist
        """
        insert_stmt = insert(Categories).values({'category_name': category_name}).returning(Categories.category_name)
        with self.session_factory() as session:
            inserted_row = session.execute(insert_stmt).fetchall()
            session.commit()
            return super(Categories, Categories)._transform_returning_row_into_dict(
                inserted_row[0], RETURNING_CATEGORIES_COLUMNS
            )

    def read(self) -> List[Dict]:
        """
        Reads all existing categories
        """
        select_stmt = select(Categories)
        with self.session_factory() as session:
            exec_result = session.execute(select_stmt)
            return [
                super(Categories, Categories)._transform_select_row_into_dict(
                    r, CATEGORIES_COLUMNS
                ) for r in exec_result
            ]

    def update(self, old_category: str, new_category: str) -> Dict:
        """
        Updates a category name
        """
        update_stmt = update(Categories).where(Categories.category_name == old_category).values(
            {'category_name': new_category}
        ).returning(Categories.category_id, Categories.category_name)
        with self.session_factory() as session:
            exec_result = session.execute(update_stmt).fetchall()
            session.commit()
            return super(Categories, Categories)._transform_returning_row_into_dict(
                exec_result[0], CATEGORIES_COLUMNS
            )   # IndexError: list index out of range when there is no category

    def delete(self, category: str) -> Dict:
        """
        Deletes a category
        """
        delete_stmt = delete(Categories).where(Categories.category_name == category).returning(
            Categories.category_id, Categories.category_name
        )
        with self.session_factory() as session:
            exec_result = session.execute(delete_stmt).fetchall()
            session.commit()
            return super(Categories, Categories)._transform_returning_row_into_dict(
                exec_result[0], CATEGORIES_COLUMNS
            )   # IndexError: list index out of range when there is no category
