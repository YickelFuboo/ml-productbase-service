import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.build import (
    ArchBuildArtifact,
    ArchElementToArtifact,
    ArchArtifactToArtifact,
)
from app.domains.arch_mgmt.schemes.build import (
    ArchBuildArtifactCreate,
    ArchBuildArtifactUpdate,
    ArchBuildArtifactInfo,
    ArchBuildArtifactTree,
    ArchElementToArtifactCreate,
    ArchElementToArtifactUpdate,
    ArchArtifactToArtifactCreate,
    ArchArtifactToArtifactUpdate,
)
from app.domains.arch_mgmt.services.architecture_service import ArchitectureService


class BuildService:
    """构建视图服务（BuildArtifact, ElementToArtifact, ArtifactToArtifact）"""

    # ==================== BuildArtifact ====================

    @staticmethod
    async def create_build_artifact(session: AsyncSession, data: ArchBuildArtifactCreate, user_id: str) -> ArchBuildArtifact:
        artifact = ArchBuildArtifact(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            name=data.name,
            artifact_type=data.artifact_type,
            build_command=data.build_command,
            build_environment=data.build_environment,
            description=data.description,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(artifact)
        await session.commit()
        await session.refresh(artifact)
        logging.info(f"创建构建产物 version_id={data.version_id} name={data.name} type={data.artifact_type}")
        return artifact

    @staticmethod
    async def update_build_artifact(
        session: AsyncSession, artifact_id: str, data: ArchBuildArtifactUpdate
    ) -> Optional[ArchBuildArtifact]:
        artifact = await BuildService.get_build_artifact_by_id(session, artifact_id)
        if not artifact:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(artifact, k, v)
        artifact.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(artifact)
        return artifact

    @staticmethod
    async def delete_build_artifact(session: AsyncSession, artifact_id: str) -> bool:
        artifact = await BuildService.get_build_artifact_by_id(session, artifact_id)
        if not artifact:
            return False
        await session.delete(artifact)
        await session.commit()
        logging.info(f"删除构建产物 artifact_id={artifact_id}")
        return True

    @staticmethod
    async def list_build_artifacts(
        session: AsyncSession, version_id: str, artifact_type: Optional[str] = None
    ) -> List[ArchBuildArtifact]:
        q = select(ArchBuildArtifact).where(ArchBuildArtifact.version_id == version_id).order_by(ArchBuildArtifact.created_at)
        if artifact_type:
            q = q.where(ArchBuildArtifact.artifact_type == artifact_type)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_build_artifact_by_id(session: AsyncSession, artifact_id: str) -> Optional[ArchBuildArtifact]:
        result = await session.execute(select(ArchBuildArtifact).where(ArchBuildArtifact.id == artifact_id))
        return result.scalar_one_or_none()

    # ==================== ElementToArtifact ====================

    @staticmethod
    async def create_element_to_artifact(
        session: AsyncSession, data: ArchElementToArtifactCreate
    ) -> Optional[ArchElementToArtifact]:
        element = await ArchitectureService.get_element_by_id(session, data.element_id)
        if not element or element.version_id != data.version_id:
            return None
        artifact = await BuildService.get_build_artifact_by_id(session, data.build_artifact_id)
        if not artifact or artifact.version_id != data.version_id:
            return None
        
        element_artifact = ArchElementToArtifact(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            element_id=data.element_id,
            build_artifact_id=data.build_artifact_id,
            build_order=data.build_order,
            description=data.description,
            created_at=datetime.utcnow(),
        )
        session.add(element_artifact)
        await session.commit()
        await session.refresh(element_artifact)
        logging.info(f"创建架构元素-构建产物映射 version_id={data.version_id} element_id={data.element_id} build_artifact_id={data.build_artifact_id}")
        return element_artifact

    @staticmethod
    async def update_element_to_artifact(
        session: AsyncSession, element_artifact_id: str, data: ArchElementToArtifactUpdate
    ) -> Optional[ArchElementToArtifact]:
        element_artifact = await BuildService.get_element_to_artifact_by_id(session, element_artifact_id)
        if not element_artifact:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(element_artifact, k, v)
        element_artifact.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(element_artifact)
        return element_artifact

    @staticmethod
    async def delete_element_to_artifact(session: AsyncSession, element_artifact_id: str) -> bool:
        element_artifact = await BuildService.get_element_to_artifact_by_id(session, element_artifact_id)
        if not element_artifact:
            return False
        
        await session.delete(element_artifact)
        await session.commit()
        logging.info(f"删除架构元素-构建产物映射 element_artifact_id={element_artifact_id}")
        return True

    @staticmethod
    async def list_element_to_artifacts(
        session: AsyncSession, version_id: str, element_id: Optional[str] = None, build_artifact_id: Optional[str] = None
    ) -> List[ArchElementToArtifact]:
        q = select(ArchElementToArtifact).where(ArchElementToArtifact.version_id == version_id).order_by(ArchElementToArtifact.build_order, ArchElementToArtifact.created_at)
        if element_id:
            q = q.where(ArchElementToArtifact.element_id == element_id)
        if build_artifact_id:
            q = q.where(ArchElementToArtifact.build_artifact_id == build_artifact_id)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_element_to_artifact_by_id(session: AsyncSession, element_artifact_id: str) -> Optional[ArchElementToArtifact]:
        result = await session.execute(select(ArchElementToArtifact).where(ArchElementToArtifact.id == element_artifact_id))
        return result.scalar_one_or_none()

    # ==================== ArtifactToArtifact ====================

    @staticmethod
    async def create_artifact_to_artifact(
        session: AsyncSession, data: ArchArtifactToArtifactCreate
    ) -> Optional[ArchArtifactToArtifact]:
        input_artifact = await BuildService.get_build_artifact_by_id(session, data.input_artifact_id)
        if not input_artifact or input_artifact.version_id != data.version_id:
            return None
        target_artifact = await BuildService.get_build_artifact_by_id(session, data.target_artifact_id)
        if not target_artifact or target_artifact.version_id != data.version_id:
            return None
        
        artifact_to_artifact = ArchArtifactToArtifact(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            input_artifact_id=data.input_artifact_id,
            target_artifact_id=data.target_artifact_id,
            build_order=data.build_order,
            description=data.description,
            created_at=datetime.utcnow(),
        )
        session.add(artifact_to_artifact)
        await session.commit()
        await session.refresh(artifact_to_artifact)
        logging.info(f"创建构建产物关系 version_id={data.version_id} input_artifact_id={data.input_artifact_id} target_artifact_id={data.target_artifact_id}")
        return artifact_to_artifact

    @staticmethod
    async def update_artifact_to_artifact(
        session: AsyncSession, artifact_to_artifact_id: str, data: ArchArtifactToArtifactUpdate
    ) -> Optional[ArchArtifactToArtifact]:
        artifact_to_artifact = await BuildService.get_artifact_to_artifact_by_id(session, artifact_to_artifact_id)
        if not artifact_to_artifact:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(artifact_to_artifact, k, v)
        artifact_to_artifact.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(artifact_to_artifact)
        return artifact_to_artifact

    @staticmethod
    async def delete_artifact_to_artifact(session: AsyncSession, artifact_to_artifact_id: str) -> bool:
        artifact_to_artifact = await BuildService.get_artifact_to_artifact_by_id(session, artifact_to_artifact_id)
        if not artifact_to_artifact:
            return False
        
        await session.delete(artifact_to_artifact)
        await session.commit()
        logging.info(f"删除构建产物关系 artifact_to_artifact_id={artifact_to_artifact_id}")
        return True

    @staticmethod
    async def list_artifact_to_artifacts(
        session: AsyncSession, version_id: str, input_artifact_id: Optional[str] = None, target_artifact_id: Optional[str] = None
    ) -> List[ArchArtifactToArtifact]:
        q = select(ArchArtifactToArtifact).where(ArchArtifactToArtifact.version_id == version_id).order_by(ArchArtifactToArtifact.build_order, ArchArtifactToArtifact.created_at)
        if input_artifact_id:
            q = q.where(ArchArtifactToArtifact.input_artifact_id == input_artifact_id)
        if target_artifact_id:
            q = q.where(ArchArtifactToArtifact.target_artifact_id == target_artifact_id)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_artifact_to_artifact_by_id(session: AsyncSession, artifact_to_artifact_id: str) -> Optional[ArchArtifactToArtifact]:
        result = await session.execute(select(ArchArtifactToArtifact).where(ArchArtifactToArtifact.id == artifact_to_artifact_id))
        return result.scalar_one_or_none()

    # ==================== BuildArtifact Tree ====================

    @staticmethod
    def _artifact_to_tree(
        artifact: ArchBuildArtifact,
        all_artifacts: List[ArchBuildArtifact],
        artifact_relations: List[ArchArtifactToArtifact],
    ):
        """将构建产物转换为树节点，子节点是输入产物"""
        # 找到所有以当前产物为目标产物的关系（即当前产物作为父节点）
        # target_artifact_id 是父节点（产物），input_artifact_id 是子节点（输入）
        child_relations = [r for r in artifact_relations if r.target_artifact_id == artifact.id]
        # 获取所有子输入产物
        child_artifact_ids = [r.input_artifact_id for r in child_relations]
        children = [a for a in all_artifacts if a.id in child_artifact_ids]
        # 按 build_order 和 created_at 排序
        sorted_children = sorted(
            children,
            key=lambda x: (
                next((r.build_order for r in child_relations if r.input_artifact_id == x.id), 0),
                x.created_at or datetime.min,
            ),
        )

        # 构建树节点
        data = ArchBuildArtifactInfo.model_validate(artifact).model_dump()
        data["children"] = [
            BuildService._artifact_to_tree(c, all_artifacts, artifact_relations) for c in sorted_children
        ]
        return ArchBuildArtifactTree(**data)

    @staticmethod
    async def get_build_artifacts_tree(session: AsyncSession, version_id: str):
        """获取构建产物树结构（父节点是产物，子节点是输入）"""
        # 获取所有构建产物
        result = await session.execute(
            select(ArchBuildArtifact).where(ArchBuildArtifact.version_id == version_id).order_by(ArchBuildArtifact.created_at)
        )
        all_artifacts = list(result.scalars().all())

        # 获取所有构建产物关系
        relations_result = await session.execute(
            select(ArchArtifactToArtifact).where(ArchArtifactToArtifact.version_id == version_id)
        )
        artifact_relations = list(relations_result.scalars().all())

        # 找到所有根节点：没有作为 input_artifact_id 的构建产物（即最终的产物，不是其他产物的输入）
        input_artifact_ids = {r.input_artifact_id for r in artifact_relations}
        roots = [a for a in all_artifacts if a.id not in input_artifact_ids]

        # 如果没有关系，返回所有产物作为根节点
        if not artifact_relations:
            return [
                ArchBuildArtifactTree(**ArchBuildArtifactInfo.model_validate(a).model_dump(), children=[])
                for a in sorted(roots, key=lambda x: x.created_at or datetime.min)
            ]

        # 构建树结构
        return [
            BuildService._artifact_to_tree(r, all_artifacts, artifact_relations)
            for r in sorted(roots, key=lambda x: x.created_at or datetime.min)
        ]
