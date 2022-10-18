from dataclasses import dataclass
from typing import Dict, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Integer, Column, String, select, Boolean
from sqlalchemy.orm import relationship

import orm


@dataclass
class UsersColumns:
    USER_ID = 'user_id'
    EMAIL = 'email'
    PASSWD = 'passwd'
    IS_ADMIN = 'is_admin'


USERS_COLUMNS = [
    UsersColumns.USER_ID,
    UsersColumns.EMAIL,
    UsersColumns.PASSWD,
    UsersColumns.IS_ADMIN
]

RETURNING_USERS_COLUMNS = [
    UsersColumns.EMAIL,
    UsersColumns.IS_ADMIN
]


class Users(orm.BaseTable):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    passwd = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    def create(self, user_data: Dict) -> Dict:
        """
        inserts a new user in the db if entry doesn't already exist
        :param user_data: dict with column name as keys and appropriate values
        :return: relevant info about inserted user
        """

        insert_stmt = insert(Users).values(user_data).returning(Users.email, Users.is_admin)

        with self.session_factory() as session:
            inserted_row = session.execute(insert_stmt).fetchall()
            session.commit()
            return super(Users, Users)._transform_returning_row_into_dict(inserted_row[0], RETURNING_USERS_COLUMNS)

    def read(self, identifier: str, identifier_type: str = UsersColumns.EMAIL) -> List[Dict]:
        """
        Search functionality, to search after one column value
        :param identifier: value to look for
        :param identifier_type: column to search through
        :return: all valid hits
        """
        select_stmt = select(Users).where(Users.__table__.c[identifier_type] == identifier)
        result = []
        with self.session_factory() as session:
            exec_result = session.execute(select_stmt)
            for r in exec_result:
                result.append(super(Users, Users)._transform_select_row_into_dict(r, USERS_COLUMNS))
        return result
