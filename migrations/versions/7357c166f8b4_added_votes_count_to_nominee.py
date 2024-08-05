"""added votes count to nominee

Revision ID: 7357c166f8b4
Revises: 6c0c5dbc9dbe
Create Date: 2023-11-23 08:17:52.195680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7357c166f8b4'
down_revision = '6c0c5dbc9dbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nominee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('votes_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nominee', schema=None) as batch_op:
        batch_op.drop_column('votes_count')

    # ### end Alembic commands ###