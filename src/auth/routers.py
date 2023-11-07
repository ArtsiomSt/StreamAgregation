from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Request, status

from application.cache import RedisCacheManager
from application.dependecies import get_cache_manager
from application.utils import send_email_notification
from auth.dependencis import CurrentUser, UserPdb, AdminUser
from auth.schemas import ExtendedUserScheme, RefreshToken, UserLoginData, UserRegisterScheme, UserScheme, TokenScheme
from auth.utils import create_access_token, create_refresh_token, get_refreshed_access_token, create_confirm_token

auth_router = APIRouter(prefix="/auth")

CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]


@auth_router.post("/register", response_model=ExtendedUserScheme, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterScheme, db: UserPdb):
    created_user = await db.save_one_user(user_data)
    return created_user


@auth_router.post("/token", response_model=TokenScheme)
async def login(login_data: UserLoginData, db: UserPdb):
    user = await db.check_credentials(login_data.email, login_data.password)
    if user:
        return TokenScheme(
            access_token=create_access_token(user.email),
            refresh_token=create_refresh_token(user.email),
        )
    else:
        raise HTTPException(status_code=500, detail="Unexpected authorization error")


@auth_router.post("/token/refresh", response_model=TokenScheme)
async def refresh(refresh_token: RefreshToken):
    return TokenScheme(
        access_token=get_refreshed_access_token(refresh_token.refresh_token),
        refresh_token=refresh_token.refresh_token,
    )


@auth_router.get('/me', response_model=UserScheme)
async def get_me(user: CurrentUser):
    return UserScheme(
        **user.model_dump()
    )


@auth_router.patch('/me', response_model=UserScheme)
async def change_profile_info(user: CurrentUser, new_user_data: UserScheme, db: UserPdb):
    return await db.change_user_profile(user, new_user_data)


@auth_router.get("/email/send-verify-email")
async def send_verify_email_message(user: CurrentUser, cache: CacheMngr, request: Request):
    confirm_token = create_confirm_token()
    await cache.save_to_cache(confirm_token, 300, user.email)
    await send_email_notification(
        [user.email],
        f"To confirm email use this link {request.base_url}auth/email/verify/{confirm_token}",
        "Email confirmation"
    )
    return {"detail": "message sent"}


@auth_router.get("/email/verify/{token}")
async def verify_email_address(token: str, cache: CacheMngr, db: UserPdb):
    email = await cache.get_object_from_cache(token)
    if email is None:
        raise HTTPException(status_code=400, detail='Not valid link')
    await db.confirm_user_email(email)
    return {"detail": "email verified"}


@auth_router.get('/admin')
async def check_admin_rights(user: AdminUser):
    return {'detail': 'success'}
