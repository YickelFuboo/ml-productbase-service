"""arch_element parent_id CASCADE

Revision ID: a1b2c3d4e5f6
Revises: ef1e7b7db297
Create Date: 2026-02-06

"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy import inspect


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ef1e7b7db297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _get_parent_id_fk_name(conn):
    insp = inspect(conn)
    for fk in insp.get_foreign_keys('arch_element'):
        if fk.get('constrained_columns') == ['parent_id']:
            return fk.get('name')
    return None


def upgrade() -> None:
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    fk_name = _get_parent_id_fk_name(conn)
    if not fk_name:
        return
    if dialect_name == 'postgresql':
        op.drop_constraint(fk_name, 'arch_element', type_='foreignkey')
        op.create_foreign_key(
            'arch_element_parent_id_fkey',
            'arch_element', 'arch_element',
            ['parent_id'], ['id'],
            ondelete='CASCADE'
        )
    elif dialect_name == 'mysql':
        op.drop_constraint(fk_name, 'arch_element', type_='foreignkey')
        op.create_foreign_key(
            fk_name,
            'arch_element', 'arch_element',
            ['parent_id'], ['id'],
            ondelete='CASCADE'
        )
    else:
        with op.batch_alter_table('arch_element', schema=None) as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
            batch_op.create_foreign_key(
                'arch_element_parent_id_fkey',
                'arch_element', ['parent_id'],
                ['id'], ondelete='CASCADE'
            )


def downgrade() -> None:
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    fk_name = _get_parent_id_fk_name(conn)
    if not fk_name:
        return
    if dialect_name == 'postgresql':
        op.drop_constraint(fk_name, 'arch_element', type_='foreignkey')
        op.create_foreign_key(
            'arch_element_parent_id_fkey',
            'arch_element', 'arch_element',
            ['parent_id'], ['id'],
            ondelete='SET NULL'
        )
    elif dialect_name == 'mysql':
        op.drop_constraint(fk_name, 'arch_element', type_='foreignkey')
        op.create_foreign_key(
            fk_name,
            'arch_element', 'arch_element',
            ['parent_id'], ['id'],
            ondelete='SET NULL'
        )
    else:
        with op.batch_alter_table('arch_element', schema=None) as batch_op:
            batch_op.drop_constraint(fk_name, type_='foreignkey')
            batch_op.create_foreign_key(
                'arch_element_parent_id_fkey',
                'arch_element', ['parent_id'],
                ['id'], ondelete='SET NULL'
            )
