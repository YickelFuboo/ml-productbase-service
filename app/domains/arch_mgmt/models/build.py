"""
构建关系模型：ArchBuildArtifact、ArchElementToArtifact、ArchArtifactToArtifact
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class ArchBuildArtifactType(str, Enum):
    """构建产物类型"""
    JAR = "jar"  # JAR包
    WAR = "war"  # WAR包
    DOCKER_IMAGE = "docker_image"  # Docker镜像
    BINARY = "binary"  # 二进制文件
    NPM_PACKAGE = "npm_package"  # NPM包
    PYTHON_PACKAGE = "python_package"  # Python包
    LIBRARY = "library"  # 库文件
    ZIP = "zip"  # ZIP压缩包
    TAR = "tar"  # TAR压缩包
    TAR_GZ = "tar_gz"  # TAR.GZ压缩包
    OTHER = "other"  # 其他

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchBuildArtifact(Base):
    """构建产物（二进制包）"""
    __tablename__ = "arch_build_artifact"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")

    name = Column(String(255), nullable=False, index=True, comment="构建产物名称")
    artifact_type = Column(String(32), nullable=False, index=True, comment=f"产物类型：{'|'.join(ArchBuildArtifactType.values())}")
    description = Column(Text, nullable=True, comment="说明")
    build_command = Column(Text, nullable=True, comment="构建命令")
    build_environment = Column(Text, nullable=True, comment="构建环境信息（OS、编译器版本、运行时版本等）")

    create_user_id = Column(String(36), nullable=True, index=True, comment="创建人ID")
    owner_id = Column(String(36), nullable=True, index=True, comment="数据Owner ID，默认创建人")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    element_sources = relationship("ArchElementToArtifact", back_populates="build_artifact", cascade="all, delete-orphan")
    input_artifact_relations = relationship("ArchArtifactToArtifact", foreign_keys="ArchArtifactToArtifact.target_artifact_id", back_populates="target_artifact", cascade="all, delete-orphan")
    output_artifact_relations = relationship("ArchArtifactToArtifact", foreign_keys="ArchArtifactToArtifact.input_artifact_id", back_populates="input_artifact", cascade="all, delete-orphan")
    deployment_relations = relationship("ArchArtifactToDeployment", foreign_keys="ArchArtifactToDeployment.build_artifact_id", back_populates="build_artifact", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_arch_build_artifact_version_type", "version_id", "artifact_type"),)

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "name": self.name,
            "artifact_type": self.artifact_type,
            "description": self.description,
            "build_command": self.build_command,
            "build_environment": self.build_environment,
            "create_user_id": self.create_user_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchArtifactToArtifact(Base):
    """构建产物之间的构建关系（多个输入产物构建成一个输出产物）"""
    __tablename__ = "arch_artifact_to_artifact"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    
    input_artifact_id = Column(String(36), ForeignKey("arch_build_artifact.id", ondelete="CASCADE"), nullable=False, index=True, comment="输入构建产物ID")
    target_artifact_id = Column(String(36), ForeignKey("arch_build_artifact.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标构建产物ID（由输入产物构建而成）")
    build_order = Column(Integer, default=0, nullable=False, comment="构建顺序（同一目标产物的多个输入产物）")
    description = Column(Text, nullable=True, comment="说明")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    input_artifact = relationship("ArchBuildArtifact", foreign_keys=[input_artifact_id], back_populates="output_artifact_relations")
    target_artifact = relationship("ArchBuildArtifact", foreign_keys=[target_artifact_id], back_populates="input_artifact_relations")

    __table_args__ = (
        Index("idx_arch_artifact_to_artifact_version", "version_id"),
        Index("idx_arch_artifact_to_artifact_input", "input_artifact_id"),
        Index("idx_arch_artifact_to_artifact_target", "target_artifact_id"),
        Index("uq_arch_artifact_to_artifact_version_input_target", "version_id", "input_artifact_id", "target_artifact_id", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "input_artifact_id": self.input_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "build_order": self.build_order,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchElementToArtifact(Base):
    """架构元素到构建产物的映射（多对多）"""
    __tablename__ = "arch_element_to_artifact"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    
    element_id = Column(String(36), ForeignKey("arch_element.id", ondelete="CASCADE"), nullable=False, index=True, comment="架构元素ID")
    build_artifact_id = Column(String(36), ForeignKey("arch_build_artifact.id", ondelete="CASCADE"), nullable=False, index=True, comment="构建产物ID")
    build_order = Column(Integer, default=0, nullable=False, comment="构建顺序（同一产物的多个元素）")
    description = Column(Text, nullable=True, comment="说明")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    element = relationship("ArchElement", foreign_keys=[element_id])
    build_artifact = relationship("ArchBuildArtifact", foreign_keys=[build_artifact_id], back_populates="element_sources")

    __table_args__ = (
        Index("idx_arch_element_artifact_version", "version_id"),
        Index("idx_arch_element_artifact_element", "element_id"),
        Index("idx_arch_element_artifact_build", "build_artifact_id"),
        Index("uq_arch_element_artifact_version_element_build", "version_id", "element_id", "build_artifact_id", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "element_id": self.element_id,
            "build_artifact_id": self.build_artifact_id,
            "build_order": self.build_order,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
