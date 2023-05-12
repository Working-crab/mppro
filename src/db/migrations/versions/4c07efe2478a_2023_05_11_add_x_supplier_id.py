"""2023-05-11-add x_supplier_id

Revision ID: 4c07efe2478a
Revises: 6ec637a9c9a1
Create Date: 2023-05-11 22:02:21.758890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c07efe2478a'
down_revision = '6ec637a9c9a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('x_supplier_id', sa.String(length=2048), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'x_supplier_id')
    # ### end Alembic commands ###