"""scene_mgmt tables

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-06

"""
from typing import Sequence,Union
from alembic import op
import sqlalchemy as sa


revision:str="e5f6a7b8c9d0"
down_revision:Union[str,None]="d4e5f6a7b8c9"
branch_labels:Union[str,Sequence[str],None]=None
depends_on:Union[str,Sequence[str],None]=None


def upgrade()->None:
    op.create_table(
        "scene_record",
        sa.Column("id",sa.String(length=36),nullable=False,comment="ID"),
        sa.Column("version_id",sa.String(length=36),nullable=False,comment="版本ID"),
        sa.Column("parent_id",sa.String(length=36),nullable=True,comment="父场景ID"),
        sa.Column("name",sa.String(length=255),nullable=False,comment="场景名称"),
        sa.Column("actors",sa.JSON(),nullable=True,comment="Actor（场景相关操作人员）"),
        sa.Column("description",sa.Text(),nullable=True,comment="描述"),
        sa.Column("create_user_id",sa.String(length=36),nullable=True,comment="创建人ID"),
        sa.Column("owner_id",sa.String(length=36),nullable=True,comment="数据Owner ID，默认创建人"),
        sa.Column("created_at",sa.DateTime(),nullable=False,comment="创建时间"),
        sa.Column("updated_at",sa.DateTime(),nullable=True,comment="更新时间"),
        sa.ForeignKeyConstraint(["parent_id"],["scene_record.id"],ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"],["version_record.id"],ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_scene_version_parent","scene_record",["version_id","parent_id"],unique=False)
    op.create_index(op.f("ix_scene_record_version_id"),"scene_record",["version_id"],unique=False)
    op.create_index(op.f("ix_scene_record_parent_id"),"scene_record",["parent_id"],unique=False)
    op.create_index(op.f("ix_scene_record_name"),"scene_record",["name"],unique=False)
    op.create_index(op.f("ix_scene_record_create_user_id"),"scene_record",["create_user_id"],unique=False)
    op.create_index(op.f("ix_scene_record_owner_id"),"scene_record",["owner_id"],unique=False)

    op.create_table(
        "scene_flow",
        sa.Column("id",sa.String(length=36),nullable=False,comment="ID"),
        sa.Column("version_id",sa.String(length=36),nullable=False,comment="版本ID"),
        sa.Column("scene_id",sa.String(length=36),nullable=False,comment="场景ID"),
        sa.Column("flow_type",sa.String(length=16),nullable=False,comment="流程类型：normal|exception"),
        sa.Column("name",sa.String(length=255),nullable=False,comment="流程名称"),
        sa.Column("diagram",sa.Text(),nullable=True,comment="流程图（如 mermaid/plantuml 等文本）"),
        sa.Column("diagram_description",sa.Text(),nullable=True,comment="流程图说明"),
        sa.Column("create_user_id",sa.String(length=36),nullable=True,comment="创建人ID"),
        sa.Column("owner_id",sa.String(length=36),nullable=True,comment="数据Owner ID，默认创建人"),
        sa.Column("created_at",sa.DateTime(),nullable=False,comment="创建时间"),
        sa.Column("updated_at",sa.DateTime(),nullable=True,comment="更新时间"),
        sa.ForeignKeyConstraint(["scene_id"],["scene_record.id"],ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"],["version_record.id"],ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_scene_flow_version_type","scene_flow",["version_id","flow_type"],unique=False)
    op.create_index("idx_scene_flow_scene_type","scene_flow",["scene_id","flow_type"],unique=False)
    op.create_index(op.f("ix_scene_flow_version_id"),"scene_flow",["version_id"],unique=False)
    op.create_index(op.f("ix_scene_flow_scene_id"),"scene_flow",["scene_id"],unique=False)
    op.create_index(op.f("ix_scene_flow_flow_type"),"scene_flow",["flow_type"],unique=False)
    op.create_index(op.f("ix_scene_flow_name"),"scene_flow",["name"],unique=False)
    op.create_index(op.f("ix_scene_flow_create_user_id"),"scene_flow",["create_user_id"],unique=False)
    op.create_index(op.f("ix_scene_flow_owner_id"),"scene_flow",["owner_id"],unique=False)

    op.create_table(
        "scene_flow_element",
        sa.Column("id",sa.String(length=36),nullable=False,comment="ID"),
        sa.Column("version_id",sa.String(length=36),nullable=False,comment="版本ID"),
        sa.Column("flow_id",sa.String(length=36),nullable=False,comment="流程ID"),
        sa.Column("element_id",sa.String(length=36),nullable=False,comment="关联架构元素ID"),
        sa.Column("element_order",sa.Integer(),nullable=False,comment="元素顺序"),
        sa.Column("created_at",sa.DateTime(),nullable=False,comment="创建时间"),
        sa.ForeignKeyConstraint(["element_id"],["arch_element.id"],ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["flow_id"],["scene_flow.id"],ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"],["version_record.id"],ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("uq_scene_flow_element_flow_element","scene_flow_element",["flow_id","element_id"],unique=True)
    op.create_index("idx_scene_flow_element_flow_order","scene_flow_element",["flow_id","element_order"],unique=False)
    op.create_index(op.f("ix_scene_flow_element_version_id"),"scene_flow_element",["version_id"],unique=False)
    op.create_index(op.f("ix_scene_flow_element_flow_id"),"scene_flow_element",["flow_id"],unique=False)
    op.create_index(op.f("ix_scene_flow_element_element_id"),"scene_flow_element",["element_id"],unique=False)


def downgrade()->None:
    op.drop_index(op.f("ix_scene_flow_element_element_id"),table_name="scene_flow_element")
    op.drop_index(op.f("ix_scene_flow_element_flow_id"),table_name="scene_flow_element")
    op.drop_index(op.f("ix_scene_flow_element_version_id"),table_name="scene_flow_element")
    op.drop_index("idx_scene_flow_element_flow_order",table_name="scene_flow_element")
    op.drop_index("uq_scene_flow_element_flow_element",table_name="scene_flow_element")
    op.drop_table("scene_flow_element")

    op.drop_index(op.f("ix_scene_flow_owner_id"),table_name="scene_flow")
    op.drop_index(op.f("ix_scene_flow_create_user_id"),table_name="scene_flow")
    op.drop_index(op.f("ix_scene_flow_name"),table_name="scene_flow")
    op.drop_index(op.f("ix_scene_flow_flow_type"),table_name="scene_flow")
    op.drop_index(op.f("ix_scene_flow_scene_id"),table_name="scene_flow")
    op.drop_index(op.f("ix_scene_flow_version_id"),table_name="scene_flow")
    op.drop_index("idx_scene_flow_scene_type",table_name="scene_flow")
    op.drop_index("idx_scene_flow_version_type",table_name="scene_flow")
    op.drop_table("scene_flow")

    op.drop_index(op.f("ix_scene_record_owner_id"),table_name="scene_record")
    op.drop_index(op.f("ix_scene_record_create_user_id"),table_name="scene_record")
    op.drop_index(op.f("ix_scene_record_name"),table_name="scene_record")
    op.drop_index(op.f("ix_scene_record_parent_id"),table_name="scene_record")
    op.drop_index(op.f("ix_scene_record_version_id"),table_name="scene_record")
    op.drop_index("idx_scene_version_parent",table_name="scene_record")
    op.drop_table("scene_record")

