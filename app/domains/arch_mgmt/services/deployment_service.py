import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.deployment import (
    ArchDeploymentUnit,
    ArchArtifactToDeployment,
)
from app.domains.arch_mgmt.schemes.deployment import (
    ArchDeploymentUnitCreate,
    ArchDeploymentUnitUpdate,
    ArchArtifactToDeploymentCreate,
    ArchArtifactToDeploymentUpdate,
)
from app.domains.arch_mgmt.services.build_service import BuildService


class DeploymentService:
    """部署视图服务（DeploymentUnit, ArtifactToDeployment）"""

    # ==================== DeploymentUnit ====================

    @staticmethod
    async def create_deployment_unit(session: AsyncSession, data: ArchDeploymentUnitCreate) -> ArchDeploymentUnit:
        unit = ArchDeploymentUnit(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            parent_unit_id=data.parent_unit_id,
            name=data.name,
            unit_type=data.unit_type,
            description=data.description,
            deployment_config=data.deployment_config,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(unit)
        await session.commit()
        await session.refresh(unit)
        logging.info(f"创建部署单元 version_id={data.version_id} name={data.name} type={data.unit_type}")
        return unit

    @staticmethod
    async def update_deployment_unit(
        session: AsyncSession, unit_id: str, data: ArchDeploymentUnitUpdate
    ) -> Optional[ArchDeploymentUnit]:
        unit = await DeploymentService.get_deployment_unit_by_id(session, unit_id)
        if not unit:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(unit, k, v)
        unit.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(unit)
        return unit

    @staticmethod
    async def delete_deployment_unit(session: AsyncSession, unit_id: str) -> bool:
        unit = await DeploymentService.get_deployment_unit_by_id(session, unit_id)
        if not unit:
            return False
        await session.delete(unit)
        await session.commit()
        logging.info(f"删除部署单元 unit_id={unit_id}")
        return True

    @staticmethod
    async def list_deployment_units(
        session: AsyncSession, version_id: str, unit_type: Optional[str] = None, parent_unit_id: Optional[str] = None
    ) -> List[ArchDeploymentUnit]:
        q = select(ArchDeploymentUnit).where(ArchDeploymentUnit.version_id == version_id).order_by(ArchDeploymentUnit.created_at)
        if unit_type:
            q = q.where(ArchDeploymentUnit.unit_type == unit_type)
        if parent_unit_id is not None:
            q = q.where(ArchDeploymentUnit.parent_unit_id == parent_unit_id)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_deployment_unit_by_id(session: AsyncSession, unit_id: str) -> Optional[ArchDeploymentUnit]:
        result = await session.execute(select(ArchDeploymentUnit).where(ArchDeploymentUnit.id == unit_id))
        return result.scalar_one_or_none()

    # ==================== ArtifactToDeployment ====================

    @staticmethod
    async def create_artifact_to_deployment(
        session: AsyncSession, data: ArchArtifactToDeploymentCreate
    ) -> Optional[ArchArtifactToDeployment]:
        artifact = await BuildService.get_build_artifact_by_id(session, data.build_artifact_id)
        if not artifact or artifact.version_id != data.version_id:
            return None
        unit = await DeploymentService.get_deployment_unit_by_id(session, data.deployment_unit_id)
        if not unit or unit.version_id != data.version_id:
            return None
        
        artifact_deploy = ArchArtifactToDeployment(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            build_artifact_id=data.build_artifact_id,
            deployment_unit_id=data.deployment_unit_id,
            deployment_config=data.deployment_config,
            description=data.description,
            created_at=datetime.utcnow(),
        )
        session.add(artifact_deploy)
        await session.commit()
        await session.refresh(artifact_deploy)
        logging.info(f"创建构建产物-部署单元映射 version_id={data.version_id} build_artifact_id={data.build_artifact_id} deployment_unit_id={data.deployment_unit_id}")
        return artifact_deploy

    @staticmethod
    async def update_artifact_to_deployment(
        session: AsyncSession, artifact_deploy_id: str, data: ArchArtifactToDeploymentUpdate
    ) -> Optional[ArchArtifactToDeployment]:
        artifact_deploy = await DeploymentService.get_artifact_to_deployment_by_id(session, artifact_deploy_id)
        if not artifact_deploy:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(artifact_deploy, k, v)
        artifact_deploy.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(artifact_deploy)
        return artifact_deploy

    @staticmethod
    async def delete_artifact_to_deployment(session: AsyncSession, artifact_deploy_id: str) -> bool:
        artifact_deploy = await DeploymentService.get_artifact_to_deployment_by_id(session, artifact_deploy_id)
        if not artifact_deploy:
            return False
        await session.delete(artifact_deploy)
        await session.commit()
        logging.info(f"删除构建产物-部署单元映射 artifact_deploy_id={artifact_deploy_id}")
        return True

    @staticmethod
    async def list_artifact_to_deployments(
        session: AsyncSession, version_id: str, build_artifact_id: Optional[str] = None, deployment_unit_id: Optional[str] = None
    ) -> List[ArchArtifactToDeployment]:
        q = select(ArchArtifactToDeployment).where(ArchArtifactToDeployment.version_id == version_id).order_by(ArchArtifactToDeployment.created_at)
        if build_artifact_id:
            q = q.where(ArchArtifactToDeployment.build_artifact_id == build_artifact_id)
        if deployment_unit_id:
            q = q.where(ArchArtifactToDeployment.deployment_unit_id == deployment_unit_id)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_artifact_to_deployment_by_id(session: AsyncSession, artifact_deploy_id: str) -> Optional[ArchArtifactToDeployment]:
        result = await session.execute(select(ArchArtifactToDeployment).where(ArchArtifactToDeployment.id == artifact_deploy_id))
        return result.scalar_one_or_none()
