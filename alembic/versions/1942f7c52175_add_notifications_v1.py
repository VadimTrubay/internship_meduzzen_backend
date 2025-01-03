"""add_notifications_v1

Revision ID: 1942f7c52175
Revises: 55a492f645ef
Create Date: 2024-08-14 16:49:07.286463

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1942f7c52175"
down_revision: Union[str, None] = "55a492f645ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "user_notifications", ["id"])
    op.drop_constraint(
        "user_notifications_company_member_id_fkey",
        "user_notifications",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "user_notifications",
        "company_members",
        ["company_member_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user_notifications", type_="foreignkey")
    op.create_foreign_key(
        "user_notifications_company_member_id_fkey",
        "user_notifications",
        "company_members",
        ["company_member_id"],
        ["id"],
    )
    op.drop_constraint(None, "user_notifications", type_="unique")
    # ### end Alembic commands ###
