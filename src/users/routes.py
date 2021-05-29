from fastapi import Depends, Response
from fastapi import APIRouter

from .schemas import UserDB
from ..config import SECRET

from src.users.logic import jwt_authentication, all_users, \
    on_after_forgot_password, on_after_reset_password, after_verification, after_verification_request, any_user

router = APIRouter()


@router.post("/auth/jwt/refresh")
async def refresh_jwt(response: Response, user=Depends(all_users.get_current_active_user)):
    return await jwt_authentication.get_login_response(user, response)


@router.get("/me", response_model=UserDB)
async def me(
    user: UserDB = Depends(any_user),  # type: ignore
):
    return user


router.include_router(
    all_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"])
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
