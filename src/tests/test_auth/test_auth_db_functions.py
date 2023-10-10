import pytest
from fastapi import HTTPException

from auth.exceptions import AuthException
from auth.schemas import UserRegisterScheme, UserScheme
from db.postgre_managers import AuthRelationalManager

pytest_plugins = [
    "tests.auth_fixtures",
]


@pytest.mark.asyncio
async def test_save_one_user(register_user: UserRegisterScheme, auth_pgdb: AuthRelationalManager):
    saved_user = await auth_pgdb.save_one_user(register_user)
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    assert register_user.email == user_from_db.email
    assert saved_user.id == user_from_db.id
    with pytest.raises(HTTPException):
        await auth_pgdb.save_one_user(register_user)


@pytest.mark.asyncio
async def test_check_credentials(register_user: UserRegisterScheme, auth_pgdb: AuthRelationalManager):
    logged_user = await auth_pgdb.check_credentials(register_user.email, register_user.password)
    assert logged_user.email == register_user.email
    assert logged_user.username == register_user.username
    with pytest.raises(HTTPException):  # wrong password check
        await auth_pgdb.check_credentials(register_user.email, register_user.password + "wrong_pass")
    with pytest.raises(HTTPException):  # wrong login check
        await auth_pgdb.check_credentials(register_user.email + "no_such_mail", register_user.password)
    with pytest.raises(HTTPException):  # wrong everything check
        await auth_pgdb.check_credentials(register_user.email + "no_such_mail", register_user.password + "wrong_pass")


@pytest.mark.asyncio
async def test_get_on_user_by_email(register_user: UserRegisterScheme, auth_pgdb: AuthRelationalManager):
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    assert user_from_db.email == register_user.email
    assert user_from_db.username == register_user.username
    with pytest.raises(AuthException):
        await auth_pgdb.get_one_user_by_email(register_user.email+"no_such_mail")


@pytest.mark.asyncio
async def test_change_user_profile(
        register_user: UserRegisterScheme,
        auth_pgdb: AuthRelationalManager,
        new_user_profile: UserScheme
):
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    await auth_pgdb.change_user_profile(user_from_db, new_user_profile)
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    assert user_from_db.email == register_user.email
    assert user_from_db.email != new_user_profile.email
    assert user_from_db.username == new_user_profile.username
    assert user_from_db.first_name == new_user_profile.first_name
    assert user_from_db.last_name == new_user_profile.last_name


@pytest.mark.asyncio
async def test_confirm_user_email(register_user: UserRegisterScheme, auth_pgdb: AuthRelationalManager):
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    assert not user_from_db.is_email_verified
    result = await auth_pgdb.confirm_user_email(user_from_db.email)
    assert result
    user_from_db = await auth_pgdb.get_one_user_by_email(register_user.email)
    assert user_from_db.is_email_verified
