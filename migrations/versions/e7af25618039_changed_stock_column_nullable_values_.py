"""changed stock column nullable values for high/low/lastupdateddate

Revision ID: e7af25618039
Revises: 116609a6d9a7
Create Date: 2024-10-08 21:12:48.788804

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e7af25618039'
down_revision = '116609a6d9a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('daily_high',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True)
        batch_op.alter_column('daily_low',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stock', schema=None) as batch_op:
        batch_op.alter_column('daily_low',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False)
        batch_op.alter_column('daily_high',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False)

    # ### end Alembic commands ###
