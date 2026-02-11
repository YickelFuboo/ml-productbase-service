"""fix deployment unit and interface parent cascade delete

Revision ID: b2c3d4e5f6a7
Revises: a7b8c9d0e1f2
Create Date: 2026-02-06

"""
from typing import Sequence,Union
from alembic import op
from sqlalchemy import inspect


revision:str="b2c3d4e5f6a7"
down_revision:Union[str,None]="a7b8c9d0e1f2"
branch_labels:Union[str,Sequence[str],None]=None
depends_on:Union[str,Sequence[str],None]=None


def _get_fk_name(conn,table_name,column_name):
    insp=inspect(conn)
    for fk in insp.get_foreign_keys(table_name):
        if fk.get("constrained_columns")==[column_name]:
            return fk.get("name")
    return None


def upgrade()->None:
    conn=op.get_bind()
    dialect_name=conn.dialect.name

    fk_name_deploy=_get_fk_name(conn,"arch_deployment_unit","parent_unit_id")
    if fk_name_deploy:
        if dialect_name=="postgresql":
            op.drop_constraint(fk_name_deploy,"arch_deployment_unit",type_="foreignkey")
            op.create_foreign_key(
                "arch_deployment_unit_parent_unit_id_fkey",
                "arch_deployment_unit","arch_deployment_unit",
                ["parent_unit_id"],["id"],
                ondelete="CASCADE"
            )
        elif dialect_name=="mysql":
            op.drop_constraint(fk_name_deploy,"arch_deployment_unit",type_="foreignkey")
            op.create_foreign_key(
                fk_name_deploy,
                "arch_deployment_unit","arch_deployment_unit",
                ["parent_unit_id"],["id"],
                ondelete="CASCADE"
            )
        else:
            with op.batch_alter_table("arch_deployment_unit",schema=None) as batch_op:
                batch_op.drop_constraint(fk_name_deploy,type_="foreignkey")
                batch_op.create_foreign_key(
                    "arch_deployment_unit_parent_unit_id_fkey",
                    "arch_deployment_unit",["parent_unit_id"],
                    ["id"],ondelete="CASCADE"
                )

    fk_name_interface=_get_fk_name(conn,"arch_interface","parent_id")
    if fk_name_interface:
        if dialect_name=="postgresql":
            op.drop_constraint(fk_name_interface,"arch_interface",type_="foreignkey")
            op.create_foreign_key(
                "arch_interface_parent_id_fkey",
                "arch_interface","arch_interface",
                ["parent_id"],["id"],
                ondelete="CASCADE"
            )
        elif dialect_name=="mysql":
            op.drop_constraint(fk_name_interface,"arch_interface",type_="foreignkey")
            op.create_foreign_key(
                fk_name_interface,
                "arch_interface","arch_interface",
                ["parent_id"],["id"],
                ondelete="CASCADE"
            )
        else:
            with op.batch_alter_table("arch_interface",schema=None) as batch_op:
                batch_op.drop_constraint(fk_name_interface,type_="foreignkey")
                batch_op.create_foreign_key(
                    "arch_interface_parent_id_fkey",
                    "arch_interface",["parent_id"],
                    ["id"],ondelete="CASCADE"
                )


def downgrade()->None:
    conn=op.get_bind()
    dialect_name=conn.dialect.name

    fk_name_deploy=_get_fk_name(conn,"arch_deployment_unit","parent_unit_id")
    if fk_name_deploy:
        if dialect_name=="postgresql":
            op.drop_constraint(fk_name_deploy,"arch_deployment_unit",type_="foreignkey")
            op.create_foreign_key(
                "arch_deployment_unit_parent_unit_id_fkey",
                "arch_deployment_unit","arch_deployment_unit",
                ["parent_unit_id"],["id"],
                ondelete="SET NULL"
            )
        elif dialect_name=="mysql":
            op.drop_constraint(fk_name_deploy,"arch_deployment_unit",type_="foreignkey")
            op.create_foreign_key(
                fk_name_deploy,
                "arch_deployment_unit","arch_deployment_unit",
                ["parent_unit_id"],["id"],
                ondelete="SET NULL"
            )
        else:
            with op.batch_alter_table("arch_deployment_unit",schema=None) as batch_op:
                batch_op.drop_constraint(fk_name_deploy,type_="foreignkey")
                batch_op.create_foreign_key(
                    "arch_deployment_unit_parent_unit_id_fkey",
                    "arch_deployment_unit",["parent_unit_id"],
                    ["id"],ondelete="SET NULL"
                )

    fk_name_interface=_get_fk_name(conn,"arch_interface","parent_id")
    if fk_name_interface:
        if dialect_name=="postgresql":
            op.drop_constraint(fk_name_interface,"arch_interface",type_="foreignkey")
            op.create_foreign_key(
                "arch_interface_parent_id_fkey",
                "arch_interface","arch_interface",
                ["parent_id"],["id"],
                ondelete="SET NULL"
            )
        elif dialect_name=="mysql":
            op.drop_constraint(fk_name_interface,"arch_interface",type_="foreignkey")
            op.create_foreign_key(
                fk_name_interface,
                "arch_interface","arch_interface",
                ["parent_id"],["id"],
                ondelete="SET NULL"
            )
        else:
            with op.batch_alter_table("arch_interface",schema=None) as batch_op:
                batch_op.drop_constraint(fk_name_interface,type_="foreignkey")
                batch_op.create_foreign_key(
                    "arch_interface_parent_id_fkey",
                    "arch_interface",["parent_id"],
                    ["id"],ondelete="SET NULL"
                )
