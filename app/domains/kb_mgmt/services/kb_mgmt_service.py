import logging
from datetime import datetime
from typing import List,Optional
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.domains.kb_mgmt.models.knowledge_base import KbCategory,VersionKbRecord
from app.domains.kb_mgmt.schemes.kb_mgmt import CreateVersionKb,UpdateVersionKb,VersionKbInfo,VersionKbCategoryGroup,VersionKbListResponse
from app.domains.product_mgmt.models.products import VersionRecord


class KbMgmtService:
    """版本下知识库管理：仅管理版本与知识库的绑定及分类"""

    @staticmethod
    async def _get_version(db:AsyncSession,version_id:str)->Optional[VersionRecord]:
        result=await db.execute(select(VersionRecord).where(VersionRecord.id==version_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _to_info(rec:VersionKbRecord)->VersionKbInfo:
        return VersionKbInfo.model_validate(rec)

    @staticmethod
    async def list_categories()->List[dict]:
        return [{"value":v,"display_name":KbCategory.display_name(v)} for v in KbCategory.values()]

    @staticmethod
    async def add_kb_to_version(db:AsyncSession,version_id:str,data:CreateVersionKb)->Optional[VersionKbRecord]:
        version=await KbMgmtService._get_version(db,version_id)
        if not version:
            return None
        if data.category not in KbCategory.values():
            raise ValueError(f"无效分类，可选：{','.join(KbCategory.values())}")
        rec=VersionKbRecord(
            version_id=version_id,
            kb_id=data.kb_id,
            category=data.category,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(rec)
        try:
            await db.commit()
            await db.refresh(rec)
            logging.info(f"版本 {version_id} 绑定知识库 {data.kb_id} 分类 {data.category}")
            return rec
        except IntegrityError:
            await db.rollback()
            raise ValueError("该版本下已存在相同知识库，不可重复绑定")

    @staticmethod
    async def update_version_kb(db:AsyncSession,version_id:str,item_id:str,data:UpdateVersionKb)->Optional[VersionKbRecord]:
        if data.category not in KbCategory.values():
            raise ValueError(f"无效分类，可选：{','.join(KbCategory.values())}")
        result=await db.execute(
            select(VersionKbRecord).where(
                VersionKbRecord.id==item_id,
                VersionKbRecord.version_id==version_id,
            )
        )
        rec=result.scalar_one_or_none()
        if not rec:
            return None
        rec.category=data.category
        rec.updated_at=datetime.utcnow()
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def remove_kb_from_version(db:AsyncSession,version_id:str,item_id:str)->bool:
        result=await db.execute(
            delete(VersionKbRecord).where(
                VersionKbRecord.id==item_id,
                VersionKbRecord.version_id==version_id,
            )
        )
        await db.commit()
        return result.rowcount is not None and result.rowcount > 0

    @staticmethod
    async def get_by_id(db:AsyncSession,version_id:str,item_id:str)->Optional[VersionKbRecord]:
        result=await db.execute(
            select(VersionKbRecord).where(
                VersionKbRecord.id==item_id,
                VersionKbRecord.version_id==version_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_version(db:AsyncSession,version_id:str)->VersionKbListResponse:
        version=await KbMgmtService._get_version(db,version_id)
        if not version:
            raise ValueError("版本不存在")
        result=await db.execute(
            select(VersionKbRecord).where(VersionKbRecord.version_id==version_id).order_by(VersionKbRecord.category,VersionKbRecord.created_at)
        )
        rows=result.scalars().all()
        by_category:List[VersionKbCategoryGroup]=[]
        for cat_value in KbCategory.values():
            items=[r for r in rows if r.category==cat_value]
            if items:
                by_category.append(VersionKbCategoryGroup(
                    category=cat_value,
                    category_display=KbCategory.display_name(cat_value),
                    items=[KbMgmtService._to_info(r) for r in items],
                ))
        return VersionKbListResponse(version_id=version_id,by_category=by_category)
