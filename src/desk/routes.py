from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional

from fastapi_users.models import BaseUserDB

from .services import get_appeals, get_appeal, get_comments, get_comment, \
    add_appeal, add_comment, update_appeal, update_comment, delete_appeal, delete_comment
from .schemas import AppealShort, CommentShort, Comment, AppealBase, AppealCreate, CommentCreate, CommentDB, \
    AppealUpdate
from ..users.models import UserTable
from ..users.logic import all_users

router = APIRouter()


any_user = all_users.current_user(active=True)
developer_user = all_users.current_user(active=True, superuser=True)


async def get_owner(user: UserTable = Depends(any_user)):
    if not user.is_owner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


@router.get("/", response_model=List[AppealBase], status_code=status.HTTP_200_OK)
async def appeals_list(user: UserTable = Depends(get_owner)):
    return await get_appeals()


@router.get("/{id}", response_model=AppealShort, status_code=status.HTTP_200_OK)  # TODO change to Appeal
async def appeal(id: int, user: UserTable = Depends(any_user)):
    return await get_appeal(id)


@router.post("/", response_model=AppealShort, status_code=status.HTTP_201_CREATED)
async def create_appeal(item: AppealCreate, user: UserTable = Depends(any_user)):
    return await add_appeal(item)


@router.put("/{id}", response_model=AppealShort, status_code=status.HTTP_201_CREATED)
async def update_appeal_by_id(id: int, item: AppealUpdate, user: UserTable = Depends(any_user)):
    return await update_appeal(id, item)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appeal_by_id(id: int, user: UserTable = Depends(any_user)):
    return await delete_appeal(id)


@router.get("/{id}/comments", response_model=List[CommentShort], status_code=status.HTTP_200_OK)
async def comments_list(id: int, user: UserTable = Depends(any_user)):
    return await get_comments(id)


@router.get("/{id}/comments/{pk}", response_model=Comment, status_code=status.HTTP_200_OK)
async def comment(id: int, pk: int, user: UserTable = Depends(any_user)):
    return await get_comment(id, pk)


@router.post("/{id}/comments/", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def create_comment(id: int, item: CommentCreate, user: UserTable = Depends(any_user)):
    return await add_comment(id, item)


@router.put("/{id}/comments/{pk}", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def update_comment_by_id(id: int, item: CommentCreate, user: UserTable = Depends(any_user)):
    return await update_comment(id, item)


@router.delete("/{id}/comments/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_by_id(id: int, user: UserTable = Depends(any_user)):
    return await delete_comment(id)

