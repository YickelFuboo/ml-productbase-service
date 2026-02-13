"""kb_mgmt version_kb table

Revision ID: b3c4d5e6f7a8
Revises: c8d9e0f1a2b3
Create Date: 2025-02-12

"""
from typing import Sequence,Union
from alembic import op
import sqlalchemy as sa


revision:str="b3c4d5e6f7a8"
down_revision:Union[str,None]="c8d9e0f1a2b3"
branch_labels:Union[str,Sequence[str],None]=None
depends_on:Union[str,Sequence[str],None]=None


def upgrade()->None:
    op.create_table(
        "version_kb",
        sa.Column("id",sa.String(length=36),nullable=False,comment="ID"),
        sa.Column("version_id",sa.String(length=36),nullable=False,comment="版本ID"),
        sa.Column("kb_id",sa.String(length=36),nullable=False,comment="知识库ID（来自 knowledgebase 服务）"),
        sa.Column("category",sa.String(length=32),nullable=False,comment="分类：business|solution|coding|testing|case"),
        sa.Column("created_at",sa.DateTime(),nullable=False,comment="创建时间"),
        sa.Column("updated_at",sa.DateTime(),nullable=True,comment="更新时间"),
        sa.ForeignKeyConstraint(["version_id"],["version_record.id"],ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version_id","kb_id",name="uq_version_kb_version_kb"),
    )
    op.create_index("idx_version_kb_version_category","version_kb",["version_id","category"],unique=False)
    op.create_index(op.f("ix_version_kb_version_id"),"version_kb",["version_id"],unique=False)
    op.create_index(op.f("ix_version_kb_kb_id"),"version_kb",["kb_id"],unique=False)
    op.create_index(op.f("ix_version_kb_category"),"version_kb",["category"],unique=False)


def downgrade()->None:
    op.drop_index(op.f("ix_version_kb_category"),table_name="version_kb")
    op.drop_index(op.f("ix_version_kb_kb_id"),table_name="version_kb")
    op.drop_index(op.f("ix_version_kb_version_id"),table_name="version_kb")
    op.drop_index("idx_version_kb_version_category",table_name="version_kb")
    op.drop_table("version_kb")
