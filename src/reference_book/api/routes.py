from fastapi import APIRouter
from .module import router as module_router
from .software import router as software_router
from .licence import router as licence_router

router = APIRouter()


router.include_router(module_router, prefix='/modules')
router.include_router(licence_router, prefix='/licences')
router.include_router(software_router, prefix='/software')
