from fastapi import APIRouter, status
from typing import List
from .services import get_appeals, get_appeal, get_comments, get_comment, \
    add_appeal, add_comment, update_appeal, update_comment, delete_appeal, delete_comment
from .schemas import AppealShort, CommentShort, Comment, AppealBase, AppealCreate, CommentCreate, CommentDB, \
    AppealUpdate
from ..users.models import EmployeeTable

router = APIRouter()


@router.get("/", response_model=List[AppealBase], status_code=status.HTTP_200_OK)
async def appeals_list(user: Employee = Depends(fastapi_users.get_current_active_user)):
    return await get_appeals()


@router.get("/{id}", response_model=AppealShort, status_code=status.HTTP_200_OK)  # TODO change to Appeal
async def appeal(id: int):
    return await get_appeal(id)


@router.post("/", response_model=AppealShort, status_code=status.HTTP_201_CREATED)
async def create_appeal(item: AppealCreate):
    return await add_appeal(item)


@router.put("/{id}", response_model=AppealShort, status_code=status.HTTP_201_CREATED)
async def update_appeal_by_id(id: int, item: AppealUpdate):
    return await update_appeal(id, item)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appeal_by_id(id: int):
    return await delete_appeal(id)


@router.get("/{id}/comments", response_model=List[CommentShort], status_code=status.HTTP_200_OK)
async def comments_list(id: int):
    return await get_comments(id)


@router.get("/{id}/comments/{pk}", response_model=Comment, status_code=status.HTTP_200_OK)
async def comment(id: int, pk: int):
    return await get_comment(id, pk)


@router.post("/{id}/comments/", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def create_comment(id: int, item: CommentCreate):
    return await add_comment(id, item)


@router.put("/{id}/comments/{pk}", response_model=CommentDB, status_code=status.HTTP_201_CREATED)
async def update_comment_by_id(id: int, item: CommentCreate):
    return await update_comment(id, item)


@router.delete("/{id}/comments/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_by_id(id: int):
    return await delete_comment(id)

