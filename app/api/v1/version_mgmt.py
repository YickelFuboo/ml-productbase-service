from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.schemes.version_mgmt import CreateVersion, UpdateVersion, VersionInfo
from app.services.version_mgmt_service import VersionMgmtService

router = APIRouter(prefix="/api/v1/versions", tags=["版本配置管理"])


@router.post("", response_model=VersionInfo)
async def create_version(
    data: CreateVersion,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """新增版本"""
    try:
        record = await VersionMgmtService.create_version(db, user_id, data)
        return VersionInfo.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"新增版本失败: {str(e)}",
        )


@router.get("/list", response_model=List[VersionInfo])
async def get_version_list(
    user_id: str = Query(..., description="用户ID"),
    product_id: str = Query(None, description="所属产品ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
):
    """查询版本列表"""
    try:
        items, _ = await VersionMgmtService.get_version_list(
            db, user_id, product_id=product_id, page=page, page_size=page_size, keyword=keyword
        )
        return [VersionInfo.model_validate(r) for r in items]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询版本列表失败: {str(e)}",
        )


@router.get("/{version_id}", response_model=VersionInfo)
async def get_version(
    version_id: str,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """查询版本详情"""
    try:
        record = await VersionMgmtService.get_version_by_id(db, version_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")
        if record.create_user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限查看该版本")
        return VersionInfo.model_validate(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询版本失败: {str(e)}",
        )


@router.put("/{version_id}", response_model=VersionInfo)
async def update_version(
    version_id: str,
    data: UpdateVersion,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """修改版本"""
    try:
        record = await VersionMgmtService.update_version(db, version_id, user_id, data)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")
        return VersionInfo.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改版本失败: {str(e)}",
        )


@router.delete("/{version_id}")
async def delete_version(
    version_id: str,
    user_id: str = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
):
    """删除版本"""
    try:
        success = await VersionMgmtService.delete_version(db, version_id, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="版本不存在")
        return {"message": "版本删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除版本失败: {str(e)}",
        )
