"""empty message

Revision ID: 2152db7558b2
Revises: 2283fb6e67b1
Create Date: 2021-05-06 20:21:02.666842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2152db7558b2'
down_revision = '2283fb6e67b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('device', sa.Column('connected', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('device', 'connected')
    # ### end Alembic commands ###
