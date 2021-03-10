"""empty message

Revision ID: d80dcae78afc
Revises: 9d8d4013671c
Create Date: 2021-03-02 03:49:50.295269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd80dcae78afc'
down_revision = '9d8d4013671c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('package_device_id_fkey', 'package', type_='foreignkey')
    op.create_foreign_key(None, 'package', 'device', ['device_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'package', type_='foreignkey')
    op.create_foreign_key('package_device_id_fkey', 'package', 'device', ['device_id'], ['id'])
    # ### end Alembic commands ###
