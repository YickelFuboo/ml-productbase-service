import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class ProductRecord(Base):
    """产品配置模型"""
    __tablename__ = "product_record"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    name = Column(String(255), nullable=False, index=True, comment="产品名称")
    description = Column(Text, nullable=True, comment="描述")
    product_define = Column(Text, nullable=True, comment="产品定义，一般为MD文档，描述产品定位、周边关系等")
    create_user_id = Column(String(36), nullable=False, index=True, comment="创建人ID")
    owner_id = Column(String(36), nullable=True, index=True, comment="数据Owner ID，默认创建人")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    versions = relationship("VersionRecord", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "product_define": self.product_define,
            "create_user_id": self.create_user_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VersionRecord(Base):
    """版本配置模型"""
    __tablename__ = "version_record"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    name = Column(String(255), nullable=False, index=True, comment="版本名称")
    product_id = Column(String(36), ForeignKey("product_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属产品ID")
    create_user_id = Column(String(36), nullable=False, index=True, comment="创建人ID")
    owner_id = Column(String(36), nullable=True, index=True, comment="数据Owner ID，默认创建人")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    product = relationship("ProductRecord", back_populates="versions")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "create_user_id": self.create_user_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

