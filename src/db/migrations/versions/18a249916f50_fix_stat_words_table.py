"""fix Stat_words table

Revision ID: 18a249916f50
Revises: 7028158fda4b
Create Date: 2023-04-05 19:36:39.184937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18a249916f50'
down_revision = '7028158fda4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stat_words', sa.Column('type', sa.String(), nullable=False))
    op.drop_column('stat_words', 'word_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stat_words', sa.Column('word_type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('stat_words', 'type')
    # ### end Alembic commands ###
