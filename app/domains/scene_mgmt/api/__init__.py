from fastapi import APIRouter
from app.domains.scene_mgmt.api.scene_mgmt import router as scene_router

scene_mgmt_router=APIRouter()
scene_mgmt_router.include_router(scene_router)

__all__=["scene_mgmt_router"]

