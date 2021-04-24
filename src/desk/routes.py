from fastapi import APIRouter
from typing import List
from .services import get_appeals, get_appeal, get_comments, get_comment
from .schemas import AppealShort, Appeal, CommentShort, Comment, AppealBase

router = APIRouter()


@router.get("/", response_model=List[AppealBase])
async def appeals_list():
    return await get_appeals()


@router.get("/{id}", response_model=AppealShort)
async def appeal(id: int):
    return await get_appeal(id)


@router.get("/{id}/comments", response_model=List[CommentShort])
async def comments_list(id: int):
    return await get_comments(id)


@router.get("/{id}/comments/{pk}", response_model=Comment)
async def comment(id: int, pk: int):
    return await get_comment(id, pk)
