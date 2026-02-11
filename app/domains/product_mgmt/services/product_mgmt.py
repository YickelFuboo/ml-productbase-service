import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.domains.product_mgmt.models.products import ProductRecord, VersionRecord
from app.domains.product_mgmt.schemes.product_mgmt import CreateProduct, UpdateProduct, CreateVersion, UpdateVersion


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
                product_define=data.product_define or None,
                create_user_id=user_id,
                owner_id=user_id,
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
            if data.product_define is not None:
                record.product_define = data.product_define
            if data.owner_id is not None:
                record.owner_id = data.owner_id
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
            if keyword and keyword.strip():
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
    async def update_version(db: AsyncSession, version_id: str, user_id: str, data: UpdateVersion) -> Optional[VersionRecord]:
        """修改版本"""
        try:
            record = await ProductMgmtService.get_version_by_id(db, version_id)
            if not record:
                return None
            if record.create_user_id != user_id:
                raise ValueError("无权限修改该版本")
            if data.name is not None:
                record.name = data.name
            if data.owner_id is not None:
                record.owner_id = data.owner_id
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
            record = await ProductMgmtService.get_version_by_id(db, version_id)
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
            if keyword and keyword.strip():
                filtered = filtered.where(VersionRecord.name.contains(keyword))
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
    async def get_product_and_version_list(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ) -> Tuple[List[ProductRecord], Dict[str, List[VersionRecord]], int]:
        """查询产品列表及每个产品下的版本列表（按创建人过滤）"""
        products, total = await ProductMgmtService.get_product_list(db, user_id, page, page_size, keyword)
        if not products:
            return [], {}, total
        product_ids = [p.id for p in products]
        
        result = await db.execute(
            select(VersionRecord)
            .where(VersionRecord.product_id.in_(product_ids), VersionRecord.create_user_id == user_id)
            .order_by(VersionRecord.created_at.desc())
        )
        all_versions = result.scalars().all()
        versions_by_product: Dict[str, List[VersionRecord]] = {pid: [] for pid in product_ids}
        for v in all_versions:
            versions_by_product[v.product_id].append(v)
        return products, versions_by_product, total