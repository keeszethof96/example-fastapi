"""add content column

Revision ID: 3bfe18a0960a
Revises: e878a193ef80
Create Date: 2023-04-12 20:24:17.402433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bfe18a0960a'
down_revision = 'e878a193ef80'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')

    pass
