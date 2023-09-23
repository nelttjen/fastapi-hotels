"""added favourite.

Revision ID: 3b19c108c191
Revises: 7c93ed621c94
Create Date: 2023-09-12 20:02:27.432134
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b19c108c191"
down_revision: Union[str, None] = "7c93ed621c94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "favourite_hotel",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["hotel_id"], ["hotel.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "hotel_id", name="unique_user_hotel_fav_constraint"),
    )
    op.create_index(op.f("ix_favourite_hotel_id"), "favourite_hotel", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_favourite_hotel_id"), table_name="favourite_hotel")
    op.drop_table("favourite_hotel")
    # ### end Alembic commands ###
