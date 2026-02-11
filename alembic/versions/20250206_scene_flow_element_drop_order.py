"""scene_flow_element drop element_order

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-02-06

"""
from typing import Sequence,Union
from alembic import op
import sqlalchemy as sa


revision:str="f6a7b8c9d0e1"
down_revision:Union[str,None]="e5f6a7b8c9d0"
branch_labels:Union[str,Sequence[str],None]=None
depends_on:Union[str,Sequence[str],None]=None


def upgrade()->None:
    op.drop_index("idx_scene_flow_element_flow_order",table_name="scene_flow_element")
    op.drop_column("scene_flow_element","element_order")


def downgrade()->None:
    op.add_column("scene_flow_element",sa.Column("element_order",sa.Integer(),nullable=False,server_default="0",comment="元素顺序"))
    op.create_index("idx_scene_flow_element_flow_order","scene_flow_element",["flow_id","element_order"],unique=False)
