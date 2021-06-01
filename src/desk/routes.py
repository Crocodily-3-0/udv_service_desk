from fastapi import APIRouter, status, Depends, Response, HTTPException, UploadFile, File
from typing import List, Union

from .services import get_all_appeals, get_appeal, get_comments, get_comment, \
    add_appeal, add_comment, update_appeal, update_comment, delete_comment, get_appeals_page, upload_attachment, \
    delete_attachment, get_attachment, update_dev_appeal, check_access
from .schemas import Appeal, CommentShort, Comment, AppealCreate, CommentCreate, CommentDB, \
    AppealUpdate, AppealDB, AppealShort, CommentUpdate, DevAppeal, AttachmentDB
from ..users.models import UserTable
from ..users.logic import employee, any_user

router = APIRouter()


@router.get("/", response_model=List[AppealShort], status_code=status.HTTP_200_OK)
async def appeals_list(user: UserTable = Depends(any_user)):
    if user.is_superuser:
        return await get_all_appeals()
    return await get_appeals_page(user)


@router.get("/{id}", response_model=Union[Appeal, DevAppeal], status_code=status.HTTP_200_OK)
async def appeal(id: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await get_appeal(id, user)


@router.post("/", response_model=AppealDB, status_code=status.HTTP_201_CREATED)
async def create_appeal(item: AppealCreate, user: UserTable = Depends(employee)):
    if user.is_superuser is True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return await add_appeal(item, user)


@router.patch("/{id}", response_model=AppealDB, status_code=status.HTTP_201_CREATED)
async def update_appeal_by_id(appeal_id: int, item: AppealUpdate, user: UserTable = Depends(any_user)):
    if user.is_superuser:
        return await update_dev_appeal(appeal_id, item, user)
    return await update_appeal(appeal_id, item, user)


@router.get("/{id}/comments", response_model=List[CommentShort], status_code=status.HTTP_200_OK)
async def comments_list(id: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await get_comments(id, user)


@router.get("/{id}/comments/{pk}", response_model=Comment, status_code=status.HTTP_200_OK)
async def comment(id: int, pk: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await get_comment(id, pk, user)


@router.post("/{id}/comments/", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def create_comment(id: int, item: CommentCreate, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await add_comment(id, item, user)


@router.patch("/{id}/comments/{pk}", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def update_comment_by_id(id: int, pk: int, item: CommentUpdate, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await update_comment(id, pk, item, user)


@router.delete("/{id}/comments/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_by_id(id: int, pk: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    await delete_comment(id, pk, user)


@router.get("/{id}/attachments/{pk}", status_code=status.HTTP_200_OK)
async def get_attachment_by_id(id: int, pk: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await get_attachment(pk)


@router.post("/{id}/attachments/", response_model=AttachmentDB, status_code=status.HTTP_201_CREATED)
async def upload_attachments(id: int, file: UploadFile = File(...), user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    return await upload_attachment(id, file, user)


@router.delete("/{id}/comments/{pk}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment_by_id(id: int, pk: int, user: UserTable = Depends(any_user)):
    await check_access(id, user, status.HTTP_403_FORBIDDEN)
    await delete_attachment(pk)

