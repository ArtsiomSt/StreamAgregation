from fastapi import APIRouter

from auth.dependencis import CurrentUser, UserPdb
from auth.schemas import ExtendedUserScheme, RefreshToken, UserLoginData, UserRegisterScheme, UserScheme
from auth.utils import create_access_token, create_refresh_token, get_refreshed_access_token

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", response_model=ExtendedUserScheme)
async def register(user_data: UserRegisterScheme, db: UserPdb):
    created_user = await db.save_one_user(user_data)
    return created_user


@auth_router.post("/token")
async def login(login_data: UserLoginData, db: UserPdb):
    user = await db.check_credentials(login_data.email, login_data.password)
    if user:
        return {
            "access_token": create_access_token(user.email),
            "refresh_token": create_refresh_token(user.email),
        }


@auth_router.post("/token/refresh")
async def refresh(refresh_token: RefreshToken):
    return {
        "access_token": get_refreshed_access_token(refresh_token.refresh_token),
        "refresh_token": refresh_token.refresh_token,
    }


@auth_router.get('/me', response_model=UserScheme)
async def get_me(user: CurrentUser):
    return UserScheme(
        **user.model_dump()
    )