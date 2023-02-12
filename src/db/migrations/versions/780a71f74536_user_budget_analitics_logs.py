"""User_budget_analitics_logs

Revision ID: 780a71f74536
Revises: 6e42587a68d5
Create Date: 2023-02-12 19:45:19.462442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '780a71f74536'
down_revision = '6e42587a68d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_analitics')
    op.add_column('user_budget_analitics_logs', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('user_budget_analitics_logs', sa.Column('campaign_id', sa.Integer(), nullable=False))
    op.add_column('user_budget_analitics_logs', sa.Column('date_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('user_budget_analitics_logs', sa.Column('budget', sa.Integer(), nullable=True))
    op.add_column('user_budget_analitics_logs', sa.Column('spent_money', sa.Integer(), nullable=True))
    op.add_column('user_budget_analitics_logs', sa.Column('up_money', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user_budget_analitics_logs', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'user_budget_analitics_logs', 'adverts', ['campaign_id'], ['id'])
    op.drop_column('user_budget_analitics_logs', 'title')
    op.drop_column('user_budget_analitics_logs', 'price')
    op.drop_column('user_budget_analitics_logs', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_budget_analitics_logs', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('user_budget_analitics_logs', sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user_budget_analitics_logs', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user_budget_analitics_logs', type_='foreignkey')
    op.drop_constraint(None, 'user_budget_analitics_logs', type_='foreignkey')
    op.drop_column('user_budget_analitics_logs', 'up_money')
    op.drop_column('user_budget_analitics_logs', 'spent_money')
    op.drop_column('user_budget_analitics_logs', 'budget')
    op.drop_column('user_budget_analitics_logs', 'date_time')
    op.drop_column('user_budget_analitics_logs', 'campaign_id')
    op.drop_column('user_budget_analitics_logs', 'user_id')
    op.create_table('user_analitics',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_analitics_pkey')
    )
    # ### end Alembic commands ###
