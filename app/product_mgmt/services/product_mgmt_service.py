import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.product_mgmt.models.product_record import ProductRecord
from app.product_mgmt.schemes.product_mgmt import CreateProduct, UpdateProduct


class ProductMgmtService:
    """产品配置管理服务"""

    @staticmethod
    async def create_product(db: AsyncSession, user_id: str, data: CreateProduct) -> ProductRecord:
        """新增产品"""
        try:
            record = ProductRecord(
                id=str(uuid.uuid4()),
                name=data.name,
                description=data.description or None,
                create_user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
            logging.info(f"创建产品: {record.name}, 创建人: {user_id}")
            return record
            
        except Exception as e:
            logging.error(f"创建产品失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: str) -> Optional[ProductRecord]:
        """根据ID查询产品"""
        try:
            result = await db.execute(select(ProductRecord).where(ProductRecord.id == product_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"查询产品失败: {e}")
            raise

    @staticmethod
    async def get_product_list(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ) -> tuple[List[ProductRecord], int]:
        """查询产品列表（按创建人过滤）"""
        try:
            filtered = select(ProductRecord).where(ProductRecord.create_user_id == user_id)
            if keyword:
                filtered = filtered.where(
                    ProductRecord.name.contains(keyword) | (ProductRecord.description.isnot(None) & ProductRecord.description.contains(keyword))
                )
            total_result = await db.execute(select(func.count()).select_from(filtered.subquery()))
            total = total_result.scalar() or 0
            result = await db.execute(
                filtered.order_by(ProductRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
            )
            items = result.scalars().all()
            return items, total
        except Exception as e:
            logging.error(f"查询产品列表失败: {e}")
            raise

    @staticmethod
    async def update_product(db: AsyncSession, product_id: str, user_id: str, data: UpdateProduct) -> Optional[ProductRecord]:
        """修改产品"""
        try:
            record = await ProductMgmtService.get_product_by_id(db, product_id)
            if not record:
                return None
            if record.create_user_id != user_id:
                raise ValueError("无权限修改该产品")
            if data.name is not None:
                record.name = data.name
            if data.description is not None:
                record.description = data.description
            record.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(record)
            logging.info(f"更新产品: {record.name}")
            return record
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"更新产品失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: str, user_id: str) -> bool:
        """删除产品"""
        try:
            record = await ProductMgmtService.get_product_by_id(db, product_id)
            if not record:
                return False
            if record.create_user_id != user_id:
                raise ValueError("无权限删除该产品")
            await db.execute(delete(ProductRecord).where(ProductRecord.id == product_id))
            await db.commit()
            logging.info(f"删除产品: {record.name}")
            return True
        except ValueError:
            raise
        except Exception as e:
            logging.error(f"删除产品失败: {e}")
            await db.rollback()
            raise
