from unittest.mock import MagicMock

from core import anonymous


def test_list_books(mocker):
    service = anonymous.AnonymousUsers()
    books_mock = MagicMock()
    service.books = books_mock

    ret_val = [{'stock': 100}]
    mocked_read = mocker.patch.object(service.books, 'read', return_value=ret_val)
    result = service.list_books()

    mocked_read.assert_called_once()
    assert result[1] == 200
