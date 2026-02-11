"""scene_flow merge diagram and diagram_description to content

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-02-06

"""
from typing import Sequence,Union
from alembic import op
import sqlalchemy as sa


revision:str="a7b8c9d0e1f2"
down_revision:Union[str,None]="f6a7b8c9d0e1"
branch_labels:Union[str,Sequence[str],None]=None
depends_on:Union[str,Sequence[str],None]=None


def upgrade()->None:
    conn=op.get_bind()
    dialect_name=conn.dialect.name
    op.add_column("scene_flow",sa.Column("content",sa.Text(),nullable=True,comment="流程内容（Markdown，包含流程图和说明）"))
    if dialect_name=="postgresql":
        op.execute("""
            UPDATE scene_flow 
            SET content = COALESCE(diagram_description || E'\\n\\n', '') || COALESCE(diagram, '')
            WHERE diagram IS NOT NULL OR diagram_description IS NOT NULL
        """)
    elif dialect_name=="mysql":
        op.execute("""
            UPDATE scene_flow 
            SET content = CONCAT(COALESCE(diagram_description, ''), '\\n\\n', COALESCE(diagram, ''))
            WHERE diagram IS NOT NULL OR diagram_description IS NOT NULL
        """)
    else:
        op.execute("""
            UPDATE scene_flow 
            SET content = COALESCE(diagram_description, '') || '\\n\\n' || COALESCE(diagram, '')
            WHERE diagram IS NOT NULL OR diagram_description IS NOT NULL
        """)
    op.drop_column("scene_flow","diagram_description")
    op.drop_column("scene_flow","diagram")


def downgrade()->None:
    op.add_column("scene_flow",sa.Column("diagram",sa.Text(),nullable=True,comment="流程图（如 mermaid/plantuml 等文本）"))
    op.add_column("scene_flow",sa.Column("diagram_description",sa.Text(),nullable=True,comment="流程图说明"))
    op.execute("UPDATE scene_flow SET diagram = content WHERE content IS NOT NULL")
    op.drop_column("scene_flow","content")
