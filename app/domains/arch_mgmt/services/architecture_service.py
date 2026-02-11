import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.architecture import (
    ArchOverview,
    ArchElement,
    ArchDependency,
)
from app.domains.arch_mgmt.schemes.architecture import (
    ArchOverviewCreate,
    ArchOverviewUpdate,
    ArchElementCreate,
    ArchElementUpdate,
    ArchDependencyCreate,
    ArchDependencyUpdate,
    ArchElementTree,
    ArchElementInfo,
)


class ArchitectureService:
    """逻辑架构视图服务（Overview, Element, Dependency）"""
    # ==================== Overview ====================

    @staticmethod
    async def create_overview(session: AsyncSession, data: ArchOverviewCreate, user_id: str) -> ArchOverview:
        section_key = data.section_key or "main"
        existing = await ArchitectureService.get_overview(session, data.version_id, section_key)
        if existing:
            raise ValueError(f"该版本下已存在 section_key={section_key} 的架构说明，请使用更新接口")
        overview = ArchOverview(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            section_key=section_key,
            content=data.content,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(overview)
        await session.commit()
        await session.refresh(overview)
        logging.info(f"创建架构概览 version_id={data.version_id} section_key={section_key}")
        return overview

    @staticmethod
    async def update_overview(
        session: AsyncSession, version_id: str, section_key: str, data: ArchOverviewUpdate
    ) -> Optional[ArchOverview]:
        overview = await ArchitectureService.get_overview(session, version_id, section_key)
        if not overview:
            return None
        if data.content is not None:
            overview.content = data.content
        if data.owner_id is not None:
            overview.owner_id = data.owner_id
        overview.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(overview)
        return overview

    @staticmethod
    async def list_overviews(session: AsyncSession, version_id: str) -> List[ArchOverview]:
        result = await session.execute(
            select(ArchOverview)
            .where(ArchOverview.version_id == version_id)
            .order_by(ArchOverview.section_key, ArchOverview.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_overview(session: AsyncSession, version_id: str, section_key: str = "main") -> Optional[ArchOverview]:
        result = await session.execute(
            select(ArchOverview).where(
                ArchOverview.version_id == version_id,
                ArchOverview.section_key == section_key,
            )
        )
        return result.scalar_one_or_none()

    # ==================== Element ====================

    @staticmethod
    async def create_element(session: AsyncSession, data: ArchElementCreate, user_id: str) -> ArchElement:
        elem = ArchElement(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            parent_id=data.parent_id if data.parent_id else None,
            element_type=data.element_type,
            name=data.name,
            code=data.code,
            code_repo_url=data.code_repo_url,
            code_repo_path=data.code_repo_path,
            responsibility=data.responsibility,
            definition=data.definition,
            tech_stack=data.tech_stack,
            quality_attributes=data.quality_attributes,
            constraints=data.constraints,
            specifications=data.specifications,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(elem)
        await session.commit()
        await session.refresh(elem)
        logging.info(f"创建架构元素 version_id={data.version_id} name={data.name} type={data.element_type}")
        return elem

    @staticmethod
    async def update_element(
        session: AsyncSession, element_id: str, data: ArchElementUpdate
    ) -> Optional[ArchElement]:
        elem = await ArchitectureService.get_element_by_id(session, element_id)
        if not elem:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if "parent_id" in update_data and update_data["parent_id"] == "":
            update_data["parent_id"] = None
        for k, v in update_data.items():
            setattr(elem, k, v)
        elem.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(elem)
        return elem

    @staticmethod
    async def delete_element(session: AsyncSession, element_id: str) -> bool:
        elem = await ArchitectureService.get_element_by_id(session, element_id)
        if not elem:
            return False
        await session.delete(elem)
        await session.commit()
        logging.info(f"删除架构元素 element_id={element_id}")
        return True

    @staticmethod
    async def get_elements(
        session: AsyncSession,
        version_id: str,
        parent_id: Optional[str] = None,
        element_type: Optional[str] = None,
    ) -> List[ArchElement]:
        q = select(ArchElement).where(ArchElement.version_id == version_id).order_by(ArchElement.created_at)
        if parent_id is not None:
            q = q.where(ArchElement.parent_id == parent_id)
        if element_type:
            q = q.where(ArchElement.element_type == element_type)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    def _element_to_tree(node: ArchElement, all_elements: List[ArchElement]) -> ArchElementTree:
        children = [e for e in all_elements if e.parent_id == node.id]
        sorted_children = sorted(children, key=lambda x: x.created_at or datetime.min)
        data = ArchElementInfo.model_validate(node).model_dump()
        data["children"] = [ArchitectureService._element_to_tree(c, all_elements) for c in sorted_children]
        return ArchElementTree(**data)

    @staticmethod
    async def get_elements_tree(session: AsyncSession, version_id: str) -> List[ArchElementTree]:
        result = await session.execute(
            select(ArchElement).where(ArchElement.version_id == version_id).order_by(ArchElement.created_at)
        )
        all_elements = list(result.scalars().all())
        roots = [e for e in all_elements if e.parent_id is None]
        return [
            ArchitectureService._element_to_tree(r, all_elements)
            for r in sorted(roots, key=lambda x: x.created_at or datetime.min)
        ]

    @staticmethod
    async def get_element_by_id(session: AsyncSession, element_id: str) -> Optional[ArchElement]:
        result = await session.execute(select(ArchElement).where(ArchElement.id == element_id))
        return result.scalar_one_or_none()

    # ==================== Dependency ====================

    @staticmethod
    async def create_dependency(session: AsyncSession, data: ArchDependencyCreate, user_id: str) -> Optional[ArchDependency]:
        src = await ArchitectureService.get_element_by_id(session, data.source_element_id)
        if not src or src.version_id != data.version_id:
            return None
        tgt = await ArchitectureService.get_element_by_id(session, data.target_element_id)
        if not tgt or tgt.version_id != data.version_id:
            return None
        dep = ArchDependency(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            source_element_id=data.source_element_id,
            target_element_id=data.target_element_id,
            dependency_type=data.dependency_type,
            description=data.description,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
        )
        session.add(dep)
        await session.commit()
        await session.refresh(dep)
        logging.info(f"创建架构依赖 version_id={data.version_id} source_element={data.source_element_id} target_element={data.target_element_id}")
        return dep

    @staticmethod
    async def update_dependency(
        session: AsyncSession, dependency_id: str, data: ArchDependencyUpdate
    ) -> Optional[ArchDependency]:
        dep = await ArchitectureService.get_dependency_by_id(session, dependency_id)
        if not dep:
            return None
        if data.dependency_type is not None:
            dep.dependency_type = data.dependency_type
        if data.description is not None:
            dep.description = data.description
        if data.owner_id is not None:
            dep.owner_id = data.owner_id
        await session.commit()
        await session.refresh(dep)
        return dep

    @staticmethod
    async def delete_dependency(session: AsyncSession, dependency_id: str) -> bool:
        dep = await ArchitectureService.get_dependency_by_id(session, dependency_id)
        if not dep:
            return False
        await session.delete(dep)
        await session.commit()
        logging.info(f"删除架构依赖 dependency_id={dependency_id}")
        return True

    @staticmethod
    async def get_dependencies(session: AsyncSession, version_id: str) -> List[ArchDependency]:
        result = await session.execute(
            select(ArchDependency).where(ArchDependency.version_id == version_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_dependency_by_id(session: AsyncSession, dependency_id: str) -> Optional[ArchDependency]:
        result = await session.execute(select(ArchDependency).where(ArchDependency.id == dependency_id))
        return result.scalar_one_or_none()
