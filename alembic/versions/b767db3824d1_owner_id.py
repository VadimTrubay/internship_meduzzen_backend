"""owner_id

Revision ID: b767db3824d1
Revises: de4c19aa2fdd
Create Date: 2024-07-31 09:08:09.088804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b767db3824d1'
down_revision: Union[str, None] = 'de4c19aa2fdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'actions', ['id'])
    op.add_column('companies', sa.Column('owner_id', sa.UUID(), nullable=False))
    op.create_unique_constraint(None, 'companies', ['id'])
    op.create_foreign_key(None, 'companies', 'users', ['owner_id'], ['id'])
    op.create_unique_constraint(None, 'company_members', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'company_members', type_='unique')
    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.drop_constraint(None, 'companies', type_='unique')
    op.drop_column('companies', 'owner_id')
    op.drop_constraint(None, 'actions', type_='unique')
    # ### end Alembic commands ###
