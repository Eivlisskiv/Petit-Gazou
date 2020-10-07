"""partisans1

Revision ID: 3e11cca3444b
Revises: d4e103c6035f
Create Date: 2020-10-05 15:52:13.148178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e11cca3444b'
down_revision = 'd4e103c6035f'
branch_labels = None
depends_on = None


def upgrade():
    print('u')


def downgrade():
    print('b')
