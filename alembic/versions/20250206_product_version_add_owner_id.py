"""product_record and version_record add owner_id

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-02-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("product_record", sa.Column("owner_id", sa.String(length=36), nullable=True, comment="数据Owner ID，默认创建人"))
    op.create_index(op.f("ix_product_record_owner_id"), "product_record", ["owner_id"], unique=False)
    op.add_column("version_record", sa.Column("owner_id", sa.String(length=36), nullable=True, comment="数据Owner ID，默认创建人"))
    op.create_index(op.f("ix_version_record_owner_id"), "version_record", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_version_record_owner_id"), table_name="version_record")
    op.drop_column("version_record", "owner_id")
    op.drop_index(op.f("ix_product_record_owner_id"), table_name="product_record")
    op.drop_column("product_record", "owner_id")
