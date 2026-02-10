from fastapi import APIRouter
from app.domains.arch_mgmt.api.architecture import router as architecture_router
from app.domains.arch_mgmt.api.interfaces import router as interfaces_router
from app.domains.arch_mgmt.api.build import router as build_router
from app.domains.arch_mgmt.api.deployment import router as deployment_router
from app.domains.arch_mgmt.api.decision import router as decision_router
from app.domains.arch_mgmt.api.arch_doc import router as arch_doc_router

arch_mgmt_router = APIRouter()
arch_mgmt_router.include_router(architecture_router)
arch_mgmt_router.include_router(interfaces_router)
arch_mgmt_router.include_router(build_router)
arch_mgmt_router.include_router(deployment_router)
arch_mgmt_router.include_router(decision_router)
arch_mgmt_router.include_router(arch_doc_router)

__all__ = ["arch_mgmt_router"]
