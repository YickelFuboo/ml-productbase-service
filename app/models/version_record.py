import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class VersionRecord(Base):
    """版本配置模型"""
    __tablename__ = "version_record"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    name = Column(String(255), nullable=False, index=True, comment="版本名称")
    product_id = Column(String(36), ForeignKey("product_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属产品ID")
    description = Column(Text, nullable=True, comment="描述")
    create_user_id = Column(String(36), nullable=False, index=True, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    product = relationship("ProductRecord", back_populates="versions")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "description": self.description,
            "create_user_id": self.create_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
