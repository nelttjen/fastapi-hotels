"""user_add_is_active

Revision ID: 459d815c891c
Revises: 9033f52e88a2
Create Date: 2023-09-07 15:34:45.130048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '459d815c891c'
down_revision: Union[str, None] = '9033f52e88a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_active', sa.Boolean(), server_default='FALSE', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_active')
    # ### end Alembic commands ###
