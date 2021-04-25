from fastapi import Depends, Response
from fastapi import APIRouter
from ..config import SECRET

from src.users.logic import jwt_authentication, employee_users, developer_users, \
    on_after_forgot_password, on_after_reset_password, after_verification, after_verification_request

router = APIRouter()


@router.post("/auth/jwt/refresh")
async def refresh_jwt(response: Response, user=Depends(employee_users.get_current_active_user)):
    return await jwt_authentication.get_login_response(user, response)


router.include_router(
    employee_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"])
router.include_router(
    employee_users.get_register_router(),
    prefix="/auth",
    tags=["auth"])
router.include_router(
    employee_users.get_reset_password_router(
        SECRET,
        after_forgot_password=on_after_forgot_password,
        after_reset_password=on_after_reset_password),
    prefix="/auth",
    tags=["auth"])
router.include_router(
    employee_users.get_users_router(),
    prefix="/users",
    tags=["users"])
router.include_router(
    employee_users.get_verify_router(
        SECRET,
        after_verification_request=after_verification_request,
        after_verification=after_verification),
    prefix="/auth",
    tags=["auth"])


router.include_router(
    developer_users.get_auth_router(jwt_authentication),
    prefix="/developers/auth/jwt",
    tags=["dev_auth"])
router.include_router(
    developer_users.get_register_router(),
    prefix="/developers/auth",
    tags=["dev_auth"])
router.include_router(
    developer_users.get_reset_password_router(
        SECRET,
        after_forgot_password=on_after_forgot_password,
        after_reset_password=on_after_reset_password),
    prefix="/developers/auth",
    tags=["dev_auth"])
router.include_router(
    developer_users.get_users_router(),
    prefix="/developers",
    tags=["developers"])
router.include_router(
    developer_users.get_verify_router(
        SECRET,
        after_verification_request=after_verification_request,
        after_verification=after_verification),
    prefix="/developers/auth",
    tags=["dev_auth"])


# router.include_router(employee_users.router, prefix="/users", tags=["test_user"])
