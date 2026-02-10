"""
构建视图 DTO：BuildArtifact、ElementToArtifact、ArtifactToArtifact
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domains.arch_mgmt.models.build import ArchBuildArtifactType


class ArchBuildArtifactCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    name: str = Field(..., description="构建产物名称")
    artifact_type: str = Field(..., description=f"产物类型：{'|'.join(ArchBuildArtifactType.values())}")
    build_command: Optional[str] = Field(None, description="构建命令")
    build_environment: Optional[str] = Field(None, description="构建环境信息（OS、编译器版本、运行时版本等）")
    description: Optional[str] = Field(None, description="说明")


class ArchBuildArtifactUpdate(BaseModel):
    name: Optional[str] = None
    artifact_type: Optional[str] = None
    build_command: Optional[str] = None
    build_environment: Optional[str] = None
    description: Optional[str] = None


class ArchBuildArtifactInfo(BaseModel):
    id: str
    version_id: str
    name: str
    artifact_type: str
    build_command: Optional[str] = None
    build_environment: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchArtifactToArtifactCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    input_artifact_id: str = Field(..., description="输入构建产物ID")
    target_artifact_id: str = Field(..., description="目标构建产物ID（由输入产物构建而成）")
    build_order: int = Field(0, description="构建顺序（同一目标产物的多个输入产物）")
    description: Optional[str] = Field(None, description="说明")


class ArchArtifactToArtifactUpdate(BaseModel):
    build_order: Optional[int] = None
    description: Optional[str] = None


class ArchArtifactToArtifactInfo(BaseModel):
    id: str
    version_id: str
    input_artifact_id: str
    target_artifact_id: str
    build_order: int
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchElementToArtifactCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    element_id: str = Field(..., description="架构元素ID")
    build_artifact_id: str = Field(..., description="构建产物ID")
    build_order: int = Field(0, description="构建顺序（同一产物的多个元素）")
    description: Optional[str] = Field(None, description="说明")


class ArchElementToArtifactUpdate(BaseModel):
    build_order: Optional[int] = None
    description: Optional[str] = None


class ArchElementToArtifactInfo(BaseModel):
    id: str
    version_id: str
    element_id: str
    build_artifact_id: str
    build_order: int = 0
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
