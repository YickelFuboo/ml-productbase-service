"""arch_decision drop owner_id

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_arch_decision_owner_id"), table_name="arch_decision")
    op.drop_column("arch_decision", "owner_id")


def downgrade() -> None:
    op.add_column("arch_decision", sa.Column("owner_id", sa.String(length=36), nullable=True, comment="数据Owner ID，默认创建人"))
    op.create_index(op.f("ix_arch_decision_owner_id"), "arch_decision", ["owner_id"], unique=False)
