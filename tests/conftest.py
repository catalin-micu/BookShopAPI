from unittest.mock import MagicMock

import pytest
from core import admins, registered_users


@pytest.fixture
def admins_service():
    service = admins.Admins()
    categories_mock = MagicMock()
    service.categories = categories_mock

    books_mock = MagicMock()
    service.books = books_mock

    return service


@pytest.fixture
def registered_users_service():
    service = registered_users.RegisteredUsers()
    books_mock = MagicMock()
    service.books = books_mock

    carts_mock = MagicMock()
    service.carts = carts_mock

    return service
