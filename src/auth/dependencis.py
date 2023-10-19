from typing import Annotated

from db.postgre_managers import AuthRelationalManager
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from auth.exceptions import AuthException
from auth.schemas import ExtendedUserScheme, TokenPayload

from .utils import ALGORITHM, JWT_SECRET_KEY


async def get_auth_pdb() -> AuthRelationalManager:
    manager = AuthRelationalManager()
    try:
        await manager.connect_to_database()
        yield manager
    finally:
        await manager.close_database_connection()


UserPdb = Annotated[AuthRelationalManager, Depends(get_auth_pdb)]


reusable_oauth = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


async def get_current_user(db: UserPdb, token: str = Depends(reusable_oauth)) -> ExtendedUserScheme:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(subject=payload.get("sub"), expire=payload.get("exp"))
    except jwt.ExpiredSignatureError:
        print('exp')
        raise AuthException("Token expired")
    except (jwt.JWTError, ValidationError):
        print('valid')
        raise AuthException("Could not validate credentials")
    current_user = await db.get_one_user_by_email(token_payload.subject)
    return current_user


CurrentUser = Annotated[ExtendedUserScheme, Depends(get_current_user)]
