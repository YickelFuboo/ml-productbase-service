"""arch tables add create_user_id and owner_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = [
    "arch_overview",
    "arch_element",
    "arch_dependency",
    "arch_build_artifact",
    "arch_decision",
    "arch_interface",
    "arch_deployment_unit",
]


def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(table_name, sa.Column("create_user_id", sa.String(length=36), nullable=True, comment="创建人ID"))
        op.add_column(table_name, sa.Column("owner_id", sa.String(length=36), nullable=True, comment="数据Owner ID，默认创建人"))
        op.create_index(op.f(f"ix_{table_name}_create_user_id"), table_name, ["create_user_id"], unique=False)
        op.create_index(op.f(f"ix_{table_name}_owner_id"), table_name, ["owner_id"], unique=False)


def downgrade() -> None:
    for table_name in TABLES:
        op.drop_index(op.f(f"ix_{table_name}_owner_id"), table_name=table_name)
        op.drop_index(op.f(f"ix_{table_name}_create_user_id"), table_name=table_name)
        op.drop_column(table_name, "owner_id")
        op.drop_column(table_name, "create_user_id")
