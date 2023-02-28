"""Subscribtion

Revision ID: b4df955a330c
Revises: db8ae22db4c9
Create Date: 2023-02-01 10:53:10.551794

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b4df955a330c'
down_revision = 'db8ae22db4c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'start_date')
    op.drop_column('subscriptions', 'end_date')
    op.add_column('users', sa.Column('sub_start_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('sub_end_date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'sub_end_date')
    op.drop_column('users', 'sub_start_date')
    op.add_column('subscriptions', sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('subscriptions', sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###