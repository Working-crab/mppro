"""2023_05_15_16:25_Create GPT_Transaction and update subs

Revision ID: 4f92abe37977
Revises: 4c07efe2478a
Create Date: 2023-05-15 17:24:03.344425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f92abe37977'
down_revision = '4c07efe2478a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gpt_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('amount', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('subscriptions', sa.Column('tokens_get', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'tokens_get')
    op.drop_table('gpt_transactions')
    # ### end Alembic commands ###