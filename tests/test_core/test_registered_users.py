from unittest.mock import call

import pytest
from core import registered_users


def test_list_books(mocker, registered_users_service):
    ret_val = [{'stock': 100}]
    mocked_read = mocker.patch.object(registered_users_service.books, 'read', return_value=ret_val)
    result = registered_users_service.list_books()

    mocked_read.assert_called_once()
    assert result[1] == 200


def test_add_book_to_cart(mocker, registered_users_service):
    ret_val = {'cart_id': 3}
    mocker.patch('microservice_apis.scheduler')
    mocker.patch('core.registered_users.RegisteredUsers._validate_book_stock', return_value={'stock': 3})
    mocked_create = mocker.patch.object(registered_users_service.carts, 'create', return_value=ret_val)
    result = registered_users_service.add_book_to_cart('e', 1)

    mocked_create.asswert_called_once()
    assert result == ({'email': 'e', 'message': 'Book added to user cart'}, 201)


@pytest.mark.parametrize(
    'error, error_text, status_code',
    [
        (ValueError, 'some text', 404),
        (Exception, 'some other text', 403)
    ]
)
def test_add_book_to_cart_raises(mocker, registered_users_service, error, error_text, status_code):
    mocked_validate = mocker.patch(
        'core.registered_users.RegisteredUsers._validate_book_stock', side_effect=error(error_text)
    )
    result = registered_users_service.add_book_to_cart('e', 1)

    mocked_validate.asser_called_once()
    assert result[1] == status_code
    assert error_text == result[0]['message']


def test_validate_book_stock(mocker, registered_users_service):
    mocker.patch.object(registered_users_service.books, 'read', return_value=[{'stock': 3}])
    registered_users_service._validate_book_stock(1)


@pytest.mark.parametrize('ret_val, error', [([], ValueError), ([{'stock': 0}], Exception)])
def test_validate_book_stock_raises(mocker, registered_users_service, ret_val, error):
    mocker.patch.object(registered_users_service.books, 'read', return_value=ret_val)
    with pytest.raises(error):
        registered_users_service._validate_book_stock(1)


def test_delete_book_from_cart(mocker, registered_users_service):
    mocker.patch('core.registered_users.RegisteredUsers._check_if_item_is_in_the_right_cart', return_value=1)
    mocked_delete = mocker.patch.object(registered_users_service.carts, 'delete')
    mocker.patch('microservice_apis.scheduler')
    mocker.patch('core.registered_users.RegisteredUsers._increase_book_stock')

    result = registered_users_service.delete_book_from_cart('e', 1)

    mocked_delete.assert_called_once()
    assert result == ({'email': 'e', 'message': 'Book deleted from user cart'}, 200)


@pytest.mark.parametrize(
    'error, error_text, status_code',
    [
        (ValueError, 'some text', 404),
        (RuntimeError, 'some other text', 404)
    ]
)
def test_delete_book_from_cart_raises(mocker, registered_users_service, error, error_text, status_code):
    mocked_validate = mocker.patch(
        'core.registered_users.RegisteredUsers._check_if_item_is_in_the_right_cart', side_effect=error(error_text)
    )
    result = registered_users_service.delete_book_from_cart('e', 1)

    mocked_validate.asser_called_once()
    assert result[1] == status_code
    assert error_text == result[0]['message']


def test_check_if_item_is_in_the_right_cart(mocker, registered_users_service):
    mocker.patch.object(registered_users_service.carts, 'read', return_value=[{'cart_id': 3, 'book_id': 1}])
    registered_users_service._check_if_item_is_in_the_right_cart(3, 'e')


@pytest.mark.parametrize('ret_val, error', [([], ValueError), ([{'cart_id': 2}], RuntimeError)])
def test_check_if_item_is_in_the_right_cart_raises(mocker, registered_users_service, ret_val, error):
    mocker.patch.object(registered_users_service.carts, 'read', return_value=ret_val)
    with pytest.raises(error):
        registered_users_service._check_if_item_is_in_the_right_cart(1, 'e')


def test_increase_book_stock(mocker, registered_users_service):
    mocker.patch.object(registered_users_service.books, 'read', return_value=[{'stock': 1}])
    mocked_update = mocker.patch.object(registered_users_service.books, 'update')

    registered_users_service._increase_book_stock(7)
    mocked_update.assert_called_once_with(
        update_data={'stock': 2},
        identifier=7,
        identifier_type='book_id'
    )


def test_get_cart_content_empty(mocker, registered_users_service):
    mocked = mocker.patch.object(registered_users_service.carts, 'get_cart_content', return_value=[])
    result = registered_users_service.get_cart_content('e')

    assert result[1] == 404
    mocked.assert_called_once_with('e')


def test_get_cart_content(mocker, registered_users_service):
    mocked = mocker.patch.object(
        registered_users_service.carts, 'get_cart_content', return_value=[{'title': 't', 'price': 1}]
    )
    result = registered_users_service.get_cart_content('e')
    mocked.assert_called_once_with('e')
    assert result == ({'email': 'e', 'price': 1, 'books': ['t']}, 200)


def test_checkout_cart_empty(mocker, registered_users_service):
    mocked = mocker.patch.object(registered_users_service.carts, 'delete', return_value=[])
    result = registered_users_service.checkout_cart('e')

    assert result[1] == 404
    mocked.assert_called_once_with(identifier='e', identifier_type='email')


def test_checkout_cart(mocker, registered_users_service):
    mocked = mocker.patch.object(registered_users_service.carts, 'delete', return_value=[{'cart_id': 1}])
    mocker.patch('core.registered_users.RegisteredUsers._stop_cart_cleanup_jobs')
    result = registered_users_service.checkout_cart('e')

    assert result[1] == 200
    mocked.assert_called_once_with(identifier='e', identifier_type='email')


def test_stop_cart_cleanup_jobs(mocker, registered_users_service):
    mocked_method = mocker.patch('microservice_apis.scheduler.remove_job')
    registered_users_service._stop_cart_cleanup_jobs([1, 2, 3])
    calls = [call(1), call(2), call(3)]
    mocked_method.assert_has_calls(calls)


def test_global_func(mocker):
    mocked_carts_delete = mocker.patch('orm.carts.Carts.delete')
    mocked_books_read = mocker.patch('orm.books.Books.read', return_value=[{'stock': 1}])
    mocked_books_update = mocker.patch('orm.books.Books.update')

    registered_users.func(1, 1)
    mocked_carts_delete.assert_called_once()
    mocked_books_read.assert_called_once_with(filter_column='book_id', filter_values=[1])
    mocked_books_update.assert_called_once_with(
        update_data={'stock': 2},
        identifier=1,
        identifier_type='book_id'
    )
