"""
部署视图 DTO：DeploymentUnit、ArtifactToDeployment
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domains.arch_mgmt.models.deployment import ArchDeploymentUnitType


class ArchDeploymentUnitCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    parent_unit_id: Optional[str] = Field(None, description="父部署单元ID（支持层级关系）")
    name: str = Field(..., description="部署单元名称")
    unit_type: str = Field(..., description=f"单元类型：{'|'.join(ArchDeploymentUnitType.values())}")
    description: Optional[str] = Field(None, description="说明")
    deployment_config: Optional[str] = Field(None, description="部署配置（JSON）")


class ArchDeploymentUnitUpdate(BaseModel):
    parent_unit_id: Optional[str] = None
    name: Optional[str] = None
    unit_type: Optional[str] = None
    description: Optional[str] = None
    deployment_config: Optional[str] = None


class ArchDeploymentUnitInfo(BaseModel):
    id: str
    version_id: str
    parent_unit_id: Optional[str] = None
    name: str
    unit_type: str
    description: Optional[str] = None
    deployment_config: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchArtifactToDeploymentCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    build_artifact_id: str = Field(..., description="构建产物ID")
    deployment_unit_id: str = Field(..., description="部署单元ID")
    deployment_config: Optional[str] = Field(None, description="部署配置（JSON，覆盖部署单元的默认配置）")
    description: Optional[str] = Field(None, description="说明")


class ArchArtifactToDeploymentUpdate(BaseModel):
    deployment_config: Optional[str] = None
    description: Optional[str] = None


class ArchArtifactToDeploymentInfo(BaseModel):
    id: str
    version_id: str
    build_artifact_id: str
    deployment_unit_id: str
    deployment_config: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
