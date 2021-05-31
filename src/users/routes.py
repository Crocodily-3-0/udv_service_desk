from fastapi import Depends, Response, HTTPException
from fastapi import APIRouter, status
from fastapi_users.router import ErrorCode
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from .models import user_db
from .schemas import UserDB
from ..config import SECRET

from src.users.logic import jwt_authentication, all_users, \
    on_after_forgot_password, on_after_reset_password, after_verification, after_verification_request, any_user, \
    get_new_password, create_developer

router = APIRouter()


@router.post("/auth/jwt/refresh")
async def refresh_jwt(response: Response, user=Depends(all_users.get_current_active_user)):
    return await jwt_authentication.get_login_response(user, response)


@router.get("/me", response_model=UserDB)
async def me(
    user: UserDB = Depends(any_user),  # type: ignore
):
    return user


@router.get("/create_developer", response_model=UserDB)
async def developer():
    return await create_developer()


@router.post("/forgot_password", response_model=UserDB, status_code=status.HTTP_201_CREATED)
async def forgot_password(email: EmailStr):
    return get_new_password(email)


@router.post("/login")
async def login(
    response: Response, credentials: OAuth2PasswordRequestForm = Depends()
):
    user = await user_db.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    token = await jwt_authentication.get_login_response(user, response)
    return {"token": token, "user": user}


# router.include_router(
#     all_users.get_auth_router(jwt_authentication),
#     prefix="/auth/jwt",
#     tags=["auth"])
router.include_router(
    all_users.get_register_router(),
    prefix="/auth",
    tags=["auth"])
router.include_router(
    all_users.get_reset_password_router(
        SECRET,
        after_forgot_password=on_after_forgot_password,
        after_reset_password=on_after_reset_password),
    prefix="/auth",
    tags=["auth"])
# router.include_router(
#     all_users.get_users_router(),
#     prefix="/users",
#     tags=["users"])

router.include_router(
    all_users.get_verify_router(
        SECRET,
        after_verification_request=after_verification_request,
        after_verification=after_verification),
    prefix="/auth",
    tags=["auth"])
