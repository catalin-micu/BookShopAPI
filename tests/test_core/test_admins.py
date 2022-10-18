from unittest.mock import MagicMock

import pytest

from core import admins


def test_is_admin(mocker):
    def to_be_decorated():
        """some docstring"""
        pass
    mocked_users = mocker.patch('orm.books.Books')
    mocked_users.read = lambda: [{'is_admin': True}]

    decorated = admins.is_admin(to_be_decorated)
    assert decorated.__doc__ == 'some docstring'


def test_list_categories(mocker, admins_service):
    expected = ['abc', 'def']

    mocker.patch.object(admins_service.categories, 'read', return_value=expected)
    assert admins_service.list_categories() == (expected, 200)


def test_add_category(mocker, admins_service):
    ret_val = 'new_category'
    mocker.patch.object(admins_service.categories, 'create', return_value=ret_val)
    assert admins_service.add_category('a') == (ret_val, 201)


def test_add_category_with_raise(mocker, admins_service):
    mocker.patch.object(admins_service.categories, 'create', side_effect=Exception('some text'))
    result = admins_service.add_category('a')
    assert result[0]['message'] == 'some text'
    assert result[1] == 409


def test_update_category(mocker, admins_service):
    ret_val = 'updated'
    mocker.patch.object(admins_service.categories, 'update', return_value=ret_val)
    assert admins_service.update_category('old', 'new') == (ret_val, 200)


def test_update_category_with_raise(mocker, admins_service):
    mocker.patch.object(admins_service.categories, 'update', side_effect=Exception('some text'))
    result = admins_service.update_category('old', 'new')
    assert result[0]['message'] == 'Old category not found'
    assert result[1] == 404
    assert result[0]['category_name'] == 'old'


def test_delete_category(mocker, admins_service):
    ret_val = 'deleted'
    mocker.patch.object(admins_service.categories, 'delete', return_value=ret_val)
    assert admins_service.delete_category('a') == (ret_val, 200)


@pytest.mark.parametrize(
    'exception, exception_message, return_message, status_code',
    [
        (IndexError, 'some text', 'Category not found', 404),
        (Exception, 'db error', 'db error', 409)
    ]
)
def test_delete_category_raises(mocker, admins_service, exception, exception_message, return_message, status_code):
    mocker.patch.object(admins_service.categories, 'delete', side_effect=exception(exception_message))
    result = admins_service.delete_category('a')
    assert result[0]['message'] == return_message
    assert result[1] == status_code
    assert result[0]['category_name'] == 'a'


def test_list_books(mocker, admins_service):
    ret_val = 'a'
    mocker.patch.object(admins_service.books, 'read', return_value=ret_val)
    assert admins_service.list_books() == (ret_val, 200)


def test_add_book(mocker, admins_service):
    ret_val = 'added'
    mocker.patch.object(admins_service.books, 'create', return_value=ret_val)
    assert admins_service.add_book({'key': 'val'}) == (ret_val, 201)


def test_add_book_raises(mocker, admins_service):
    mocker.patch.object(admins_service.books, 'create', side_effect=Exception('db conflict'))
    result = admins_service.add_book({'k': 'v'})
    assert 'error' in result[0]
    assert result[0]['message'] == 'db conflict'


def test_update_book(mocker, admins_service):
    ret_val = 'updated'
    mocker.patch.object(admins_service.books, 'update', return_value=ret_val)
    assert admins_service.update_book({'k': 'v', 'title': 't'}) == (ret_val, 200)


@pytest.mark.parametrize(
    'error, error_message, return_message, status_code',
    [
        (IndexError, 'some text', 'Book not found', 404),
        (Exception, 'some text', 'some text', 409)
    ]
)
def test_update_book_raises(mocker, admins_service, error, error_message, return_message, status_code):
    mocker.patch.object(admins_service.books, 'update', side_effect=error(error_message))
    result = admins_service.update_book({'k': 'v', 'title': 't'})
    assert result[1] == status_code
    assert 'error' in result[0]
    assert result[0]['message'] == return_message


def test_delete_book(mocker, admins_service):
    ret_val = 'deleted'
    mocker.patch.object(admins_service.books, 'delete', return_value=ret_val)
    assert admins_service.delete_book('t') == (ret_val, 200)


@pytest.mark.parametrize(
    'error, error_message, return_message, status_code',
    [
        (IndexError, 'some text', 'Book not found', 404),
        (Exception, 'some text', 'some text', 409)
    ]
)
def test_delete_book_raises(mocker, admins_service, error, error_message, return_message, status_code):
    mocker.patch.object(admins_service.books, 'delete', side_effect=error(error_message))
    result = admins_service.delete_book('t')
    assert result[1] == status_code
    assert 'error' in result[0]
    assert result[0]['message'] == return_message
