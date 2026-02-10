"""
逻辑架构视图模型：ArchOverview、ArchElement、ArchDependency
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class ArchOverviewSectionKey(str, Enum):
    """架构说明文档的标准章节键"""
    MAIN = "main"  # 主要说明
    CONTEXT_AND_SCOPE = "context_and_scope"  # 上下文与范围
    SOLUTION_STRATEGY = "solution_strategy"  # 解决方案策略
    GLOSSARY = "glossary"  # 术语表

    @classmethod
    def values(cls):
        return cls.ordered_values()

    @classmethod
    def ordered_values(cls):
        """按文档推荐顺序返回标准 key 列表"""
        return [e.value for e in cls]

    @classmethod
    def order_for_key(cls, section_key: str) -> int:
        """标准 key 的默认顺序（0 起）；非标准 key 返回 999"""
        for i, e in enumerate(cls):
            if e.value == section_key:
                return i
        return 999


class ArchElementType(str, Enum):
    """架构元素类型（C4 + 常见架构实践）
    
    注意：这是逻辑架构层面的类型定义，与物理部署概念（ArchDeploymentUnitType）分离。
    例如：CONTAINER 在 C4 模型中指可独立部署的应用/数据存储（逻辑概念），
    而非 Docker 容器等物理部署单元。
    """
    EXTERNAL_PARTY = "external_party"  # 外部方
    EXTERNAL_SYSTEM = "external_system"  # 外部系统
    SYSTEM = "system"  # 系统（C4：系统级别）
    SUBSYSTEM = "subsystem"  # 子系统
    CONTAINER = "container"  # 容器（C4：容器级别，逻辑概念：可独立部署的应用/数据存储）
    SERVICE = "service"  # 服务
    MICROSERVICE = "microservice"  # 微服务
    API_SERVICE = "api_service"  # API服务
    WEB_APP = "web_app"  # Web应用
    BATCH_JOB = "batch_job"  # 批处理任务
    SCHEDULED_TASK = "scheduled_task"  # 定时任务
    DATABASE = "database"  # 数据库
    CACHE = "cache"  # 缓存
    QUEUE = "queue"  # 消息队列
    STORAGE = "storage"  # 存储
    SEARCH_ENGINE = "search_engine"  # 搜索引擎
    GATEWAY = "gateway"  # 网关
    API_GATEWAY = "api_gateway"  # API网关
    LOAD_BALANCER = "load_balancer"  # 负载均衡器
    CDN = "cdn"  # CDN
    FUNCTION = "function"  # 函数式服务（逻辑概念）
    COMPONENT = "component"  # 组件（C4：组件级别）
    MODULE = "module"  # 模块
    LIBRARY = "library"  # 库（逻辑概念）
    SDK = "sdk"  # SDK

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchDependencyType(str, Enum):
    """依赖关系类型（逻辑架构元素之间的依赖关系）"""
    CALLS = "calls"  # 调用（通过接口调用）
    DEPENDS_ON = "depends_on"  # 依赖于（如使用库/SDK，但不直接调用接口或访问数据）
    READS_DATA_FROM = "reads_data_from"  # 读取数据
    WRITES_DATA_TO = "writes_data_to"  # 写入数据

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchOverview(Base):
    """版本架构的叙述性说明（总览、上下文、策略、术语）"""
    __tablename__ = "arch_overview"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")

    section_key = Column(String(64), nullable=False, default="main", comment="章节键，标准键见 ArchOverviewSectionKey")
    content = Column(Text, nullable=True, comment="内容，支持 Markdown")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    __table_args__ = (Index("uq_arch_overview_version_section", "version_id", "section_key", unique=True),)

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "section_key": self.section_key,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchElement(Base):
    """架构构建块/元素（C4：System/Container/Component + 外部方）"""
    __tablename__ = "arch_element"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    parent_id = Column(String(36), ForeignKey("arch_element.id", ondelete="SET NULL"), nullable=True, index=True, comment="父元素ID")

    element_type = Column(String(32), nullable=False, index=True, comment=f"类型：{'|'.join(ArchElementType.values())}")
    name = Column(String(255), nullable=False, index=True, comment="名称")
    code = Column(String(64), nullable=True, index=True, comment="编码/代号")
    code_repo_url = Column(String(500), nullable=True, index=True, comment="代码仓地址")
    code_repo_path = Column(String(500), nullable=True, comment="代码仓内相对路径")

    responsibility = Column(Text, nullable=True, comment="职责/目的")
    definition = Column(Text, nullable=True, comment="详细定义")    
    tech_stack = Column(Text, nullable=True, comment="技术栈")
    quality_attributes = Column(Text, nullable=True, comment="质量属性")
    constraints = Column(Text, nullable=True, comment="约束")
    specifications = Column(Text, nullable=True, comment="规格")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    parent = relationship("ArchElement", remote_side="ArchElement.id", backref="children")
    out_deps = relationship("ArchDependency", foreign_keys="ArchDependency.source_element_id", back_populates="source_element", cascade="all, delete-orphan")
    in_deps = relationship("ArchDependency", foreign_keys="ArchDependency.target_element_id", back_populates="target_element", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_arch_element_version_type", "version_id", "element_type"),)

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "parent_id": self.parent_id,
            "element_type": self.element_type,
            "name": self.name,
            "code": self.code,
            "code_repo_url": self.code_repo_url,
            "code_repo_path": self.code_repo_path,
            "responsibility": self.responsibility,
            "definition": self.definition,
            "tech_stack": self.tech_stack,
            "quality_attributes": self.quality_attributes,
            "constraints": self.constraints,
            "specifications": self.specifications,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchDependency(Base):
    """架构元素间的依赖关系（element → element）"""
    __tablename__ = "arch_dependency"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")

    source_element_id = Column(String(36), ForeignKey("arch_element.id", ondelete="CASCADE"), nullable=False, index=True, comment="源架构元素ID")
    target_element_id = Column(String(36), ForeignKey("arch_element.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标架构元素ID")
    dependency_type = Column(String(48), nullable=True, index=True, comment="关系类型：calls|reads_data_from|writes_data_to|depends_on")
    description = Column(Text, nullable=True, comment="关系说明")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    source_element = relationship("ArchElement", foreign_keys=[source_element_id], back_populates="out_deps")
    target_element = relationship("ArchElement", foreign_keys=[target_element_id], back_populates="in_deps")

    __table_args__ = (
        Index("idx_arch_dep_version", "version_id"),
        Index("idx_arch_dep_element_source_target", "source_element_id", "target_element_id"),
        Index("idx_arch_dep_version_source_element", "version_id", "source_element_id"),
        Index("idx_arch_dep_version_target_element", "version_id", "target_element_id"),
        Index("uq_arch_dep_version_source_target_type", "version_id", "source_element_id", "target_element_id", "dependency_type", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "source_element_id": self.source_element_id,
            "target_element_id": self.target_element_id,
            "dependency_type": self.dependency_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
