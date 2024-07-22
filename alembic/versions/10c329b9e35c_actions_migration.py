"""actions migration

Revision ID: 10c329b9e35c
Revises: 45d67531e53c
Create Date: 2024-07-22 19:35:08.504458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10c329b9e35c'
down_revision: Union[str, None] = '45d67531e53c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'companies', ['id'])
    op.drop_constraint('companies_owner_id_fkey', 'companies', type_='foreignkey')
    op.create_foreign_key(None, 'companies', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.create_foreign_key('companies_owner_id_fkey', 'companies', 'users', ['owner_id'], ['id'])
    op.drop_constraint(None, 'companies', type_='unique')
    # ### end Alembic commands ###
