from fastapi import APIRouter, status, Depends
from typing import List

from .services import get_appeals, get_appeal, get_comments, get_comment, \
    add_appeal, add_comment, update_appeal, update_comment, delete_comment
from .schemas import Appeal, CommentShort, Comment, AppealCreate, CommentCreate, CommentDB, \
    AppealUpdate, AppealDB, AppealShort, CommentUpdate
from ..users.models import UserTable
from ..users.logic import employee

router = APIRouter()


@router.get("/", response_model=List[AppealShort], status_code=status.HTTP_200_OK)
async def appeals_list(user: UserTable = Depends(employee)):
    return await get_appeals(user)


@router.get("/{id}", response_model=Appeal, status_code=status.HTTP_200_OK)
async def appeal(id: int, user: UserTable = Depends(employee)):
    return await get_appeal(id, user)


@router.post("/", response_model=AppealDB, status_code=status.HTTP_201_CREATED)
async def create_appeal(item: AppealCreate, user: UserTable = Depends(employee)):
    return await add_appeal(item, user)


@router.put("/{id}", response_model=AppealDB, status_code=status.HTTP_201_CREATED)
async def update_appeal_by_id(id: int, item: AppealUpdate, user: UserTable = Depends(employee)):
    return await update_appeal(id, item, user)


@router.get("/{id}/comments", response_model=List[CommentShort], status_code=status.HTTP_200_OK)
async def comments_list(id: int, user: UserTable = Depends(employee)):
    return await get_comments(id, user)


@router.get("/{id}/comments/{pk}", response_model=Comment, status_code=status.HTTP_200_OK)
async def comment(id: int, pk: int, user: UserTable = Depends(employee)):
    return await get_comment(id, pk, user)


@router.post("/{id}/comments/", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def create_comment(id: int, item: CommentCreate, user: UserTable = Depends(employee)):
    return await add_comment(id, item, user)


@router.put("/{id}/comments/{pk}", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def update_comment_by_id(id: int, item: CommentUpdate, user: UserTable = Depends(employee)):
    return await update_comment(id, item, user)


@router.delete("/{id}/comments/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_by_id(id: int, user: UserTable = Depends(employee)):
    return await delete_comment(id, user)

