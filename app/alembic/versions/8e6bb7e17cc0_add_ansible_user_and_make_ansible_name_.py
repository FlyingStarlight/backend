"""Add ansible_user and make ansible_name not null

Revision ID: 8e6bb7e17cc0
Revises: a7c0a10ba304
Create Date: 2020-11-07 05:30:01.050295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e6bb7e17cc0'
down_revision = 'a7c0a10ba304'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('server', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ansible_user', sa.String(), nullable=True))
        batch_op.alter_column('ansible_name',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('server', schema=None) as batch_op:
        batch_op.alter_column('ansible_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.drop_column('ansible_user')

    # ### end Alembic commands ###
