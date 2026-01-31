import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.product_mgmt.models.version_record import VersionRecord
from app.product_mgmt.models.product_record import ProductRecord
from app.product_mgmt.schemes.version_mgmt import CreateVersion, UpdateVersion


class VersionMgmtService:
    """版本配置管理服务"""

    @staticmethod
    async def create_version(db: AsyncSession, user_id: str, data: CreateVersion) -> VersionRecord:
        """新增版本"""
        try:
            result = await db.execute(select(ProductRecord).where(ProductRecord.id == data.product_id))
            product = result.scalar_one_or_none()
            if not product:
                raise ValueError("所属产品不存在")
            if product.create_user_id != user_id:
                raise ValueError("无权限在该产品下创建版本")
            record = VersionRecord(
                id=str(uuid.uuid4()),
                name=data.name,
                product_id=data.product_id,
                description=data.description or None,
                create_user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
            logging.info(f"创建版本: {record.name}, 产品: {data.product_id}, 创建人: {user_id}")
            return record
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"创建版本失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_version_by_id(db: AsyncSession, version_id: str) -> Optional[VersionRecord]:
        """根据ID查询版本"""
        try:
            result = await db.execute(select(VersionRecord).where(VersionRecord.id == version_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"查询版本失败: {e}")
            raise

    @staticmethod
    async def get_version_list(
        db: AsyncSession,
        user_id: str,
        product_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ) -> tuple[List[VersionRecord], int]:
        """查询版本列表（按创建人过滤，可选按产品过滤）"""
        try:
            filtered = select(VersionRecord).where(VersionRecord.create_user_id == user_id)
            if product_id:
                filtered = filtered.where(VersionRecord.product_id == product_id)
            if keyword:
                filtered = filtered.where(
                    VersionRecord.name.contains(keyword) | (VersionRecord.description.isnot(None) & VersionRecord.description.contains(keyword))
                )
            total_result = await db.execute(select(func.count()).select_from(filtered.subquery()))
            total = total_result.scalar() or 0
            result = await db.execute(
                filtered.order_by(VersionRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
            )
            items = result.scalars().all()
            return items, total
        except Exception as e:
            logging.error(f"查询版本列表失败: {e}")
            raise

    @staticmethod
    async def update_version(db: AsyncSession, version_id: str, user_id: str, data: UpdateVersion) -> Optional[VersionRecord]:
        """修改版本"""
        try:
            record = await VersionMgmtService.get_version_by_id(db, version_id)
            if not record:
                return None
            if record.create_user_id != user_id:
                raise ValueError("无权限修改该版本")
            if data.name is not None:
                record.name = data.name
            if data.description is not None:
                record.description = data.description
            record.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(record)
            logging.info(f"更新版本: {record.name}")
            return record
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"更新版本失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_version(db: AsyncSession, version_id: str, user_id: str) -> bool:
        """删除版本"""
        try:
            record = await VersionMgmtService.get_version_by_id(db, version_id)
            if not record:
                return False
            if record.create_user_id != user_id:
                raise ValueError("无权限删除该版本")
            await db.execute(delete(VersionRecord).where(VersionRecord.id == version_id))
            await db.commit()
            logging.info(f"删除版本: {record.name}")
            return True
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"删除版本失败: {e}")
            await db.rollback()
            raise
