"""First revision

Revision ID: 1b4e44e99d9d
Revises: None
Create Date: 2013-08-31 23:40:36.992037

"""

# revision identifiers, used by Alembic.
revision = '1b4e44e99d9d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'migrate_version')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'migrate_version',
    sa.Column(u'repository_id', sa.VARCHAR(length=250), nullable=False),
    sa.Column(u'repository_path', sa.TEXT(), nullable=True),
    sa.Column(u'version', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint(u'repository_id')
    )
    ### end Alembic commands ###
