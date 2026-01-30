"""add product_record and version_record tables

Revision ID: 20250130_product_version
Revises:
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa


revision = "20250130_product_version"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "product_record",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("create_user_id", sa.String(36), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "version_record",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("product_record.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("create_user_id", sa.String(36), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("version_record")
    op.drop_table("product_record")
