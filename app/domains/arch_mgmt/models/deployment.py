"""
部署关系模型：ArchDeploymentUnit、ArchArtifactToDeployment
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class ArchDeploymentUnitType(str, Enum):
    """部署单元类型"""
    CLUSTER = "cluster"  # 集群
    NODE = "node"  # 节点
    NAMESPACE = "namespace"  # 命名空间
    POD = "pod"  # Pod（Kubernetes）
    CONTAINER = "container"  # 容器（Docker等）
    VM = "vm"  # 虚拟机
    INSTANCE = "instance"  # 实例
    FUNCTION = "function"  # 函数计算单元（如AWS Lambda）
    OTHER = "other"  # 其他

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchDeploymentUnit(Base):
    """部署单元"""
    __tablename__ = "arch_deployment_unit"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    
    parent_unit_id = Column(String(36), ForeignKey("arch_deployment_unit.id", ondelete="SET NULL"), nullable=True, index=True, comment="父部署单元ID（支持层级关系）")
    name = Column(String(255), nullable=False, index=True, comment="部署单元名称")
    unit_type = Column(String(32), nullable=False, index=True, comment=f"单元类型：{'|'.join(ArchDeploymentUnitType.values())}")
    description = Column(Text, nullable=True, comment="说明")
    deployment_config = Column(Text, nullable=True, comment="部署配置（JSON）")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    parent_unit = relationship("ArchDeploymentUnit", remote_side="ArchDeploymentUnit.id", backref="child_units")
    artifact_relations = relationship("ArchArtifactToDeployment", back_populates="deployment_unit", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_arch_deploy_unit_version_type", "version_id", "unit_type"),)

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "parent_unit_id": self.parent_unit_id,
            "name": self.name,
            "unit_type": self.unit_type,
            "description": self.description,
            "deployment_config": self.deployment_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchArtifactToDeployment(Base):
    """构建产物到部署单元的映射"""
    __tablename__ = "arch_artifact_to_deployment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    
    build_artifact_id = Column(String(36), ForeignKey("arch_build_artifact.id", ondelete="CASCADE"), nullable=False, index=True, comment="构建产物ID")
    deployment_unit_id = Column(String(36), ForeignKey("arch_deployment_unit.id", ondelete="CASCADE"), nullable=False, index=True, comment="部署单元ID")
    deployment_config = Column(Text, nullable=True, comment="部署配置（JSON，覆盖部署单元的默认配置）")
    description = Column(Text, nullable=True, comment="说明")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    build_artifact = relationship("ArchBuildArtifact", foreign_keys=[build_artifact_id], back_populates="deployment_relations")
    deployment_unit = relationship("ArchDeploymentUnit", foreign_keys=[deployment_unit_id], back_populates="artifact_relations")

    __table_args__ = (
        Index("idx_arch_artifact_deploy_version", "version_id"),
        Index("idx_arch_artifact_deploy_artifact", "build_artifact_id"),
        Index("idx_arch_artifact_deploy_unit", "deployment_unit_id"),
        Index("uq_arch_artifact_deploy_version_artifact_unit", "version_id", "build_artifact_id", "deployment_unit_id", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "build_artifact_id": self.build_artifact_id,
            "deployment_unit_id": self.deployment_unit_id,
            "deployment_config": self.deployment_config,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
