from unittest.mock import MagicMock

import pytest

from core import authentication


def test_register(mocker):
    expected = {'email': 'email', 'is_admin': False}, 201

    mocked_table = MagicMock()
    mocker.patch.object(mocked_table, 'create', return_value={'email': 'email', 'is_admin': False})

    auth = authentication.Authentication()
    auth.users = mocked_table
    actual = auth.register({'e': 'e', 'passwd': 'p'})

    assert actual == expected


def test_register_fails(mocker):
    expected = {'e': 'e', 'passwd': 'a', 'error': '<class \'Exception\'>', 'message': 'some text'}, 403

    mocked_table = MagicMock()
    mocker.patch.object(mocked_table, 'create', side_effect=Exception('some text'))
    mocked_hash_gen = mocker.patch('core.authentication.generate_password_hash', return_value='a')

    auth = authentication.Authentication()
    auth.users = mocked_table
    actual = auth.register({'e': 'e', 'passwd': 'p'})

    assert actual == expected
    mocked_hash_gen.assert_called_once()


@pytest.mark.parametrize(
    'expected, read_return, hash_return, access_return, refresh_return',
    [
        (({'email': 'e', 'message': 'No account associated with provided email'}, 404), [], True, None, None),
        (({'email': 'e', 'message': 'Wrong password'}, 401), [{'passwd': 'a'}], False, None, None),
        (({'email': 'e', 'access_token': 'a', 'refresh_token': 'r'}, 200), [{'passwd': 'a'}], True, 'a', 'r')
    ]
)
def test_login_no_account(mocker, expected, read_return, hash_return, access_return, refresh_return):
    mocked_table = MagicMock()
    mocker.patch.object(mocked_table, 'read', return_value=read_return)
    mocker.patch('core.authentication.check_password_hash', return_value=hash_return)
    mocker.patch('core.authentication.create_access_token', return_value=access_return)
    mocker.patch('core.authentication.create_refresh_token', return_value=refresh_return)

    auth = authentication.Authentication()
    auth.users = mocked_table
    actual = auth.login({'email': 'e', 'passwd': 'p'})

    assert actual == expected


def test_refresh(mocker):
    mocker.patch('core.authentication.create_access_token', return_value='a')
    assert authentication.Authentication().refresh('e', 'r') == ({
        'email': 'e',
        'access_token': 'a',
        'refresh_token': 'r'
    }, 200)
