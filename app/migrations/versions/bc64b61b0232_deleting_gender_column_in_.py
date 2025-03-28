"""Deleting gender column in anthropometric measurments

Revision ID: bc64b61b0232
Revises: 781077a91823
Create Date: 2025-01-16 15:01:35.864481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel



# revision identifiers, used by Alembic.
revision: str = 'bc64b61b0232'
down_revision: Union[str, None] = '781077a91823'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('anthropometricmeasurements', 'sex')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('anthropometricmeasurements', sa.Column('sex', sa.VARCHAR(length=6), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
