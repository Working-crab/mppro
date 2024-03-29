"""24-06-2023-15:13 update action-history

Revision ID: 66d42923510b
Revises: 260c8cfb2252
Create Date: 2023-06-24 15:13:44.784632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66d42923510b'
down_revision = '260c8cfb2252'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('action_history', sa.Column('status', sa.String(), nullable=False))
    op.add_column('action_history', sa.Column('initiator', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('action_history', 'initiator')
    op.drop_column('action_history', 'status')
    # ### end Alembic commands ###
