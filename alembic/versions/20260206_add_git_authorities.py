"""add git_authorities table for git auth config per provider/version

Revision ID: 20260206_git_authorities
Revises: 20260206_initial_product_version
Create Date: 2026-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260206_git_authorities"
down_revision: Union[str, None] = "20260206_initial_product_version"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "git_authorities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("version_id", sa.String(36), nullable=True, index=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("access_token", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "idx_user_provider_version",
        "git_authorities",
        ["user_id", "provider", "version_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_user_provider_version", table_name="git_authorities")
    op.drop_table("git_authorities")
